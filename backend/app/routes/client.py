from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.document import DocumentAssignment
from app.models.task import Task, ClientInquiry
from app.schemas.models import (
    DocumentAssignmentResponse,
    TaskResponse,
    ClientInquiryCreate,
    ClientInquiryResponse
)
from app.utils.auth import get_client_user

router = APIRouter(prefix="/client", tags=["client"])

@router.get("/documents", response_model=List[DocumentAssignmentResponse])
async def get_assigned_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Get documents assigned to the current user's client"""
    # Admin users can specify client_id, regular users use their own client
    client_id = current_user.client_id
    if current_user.is_admin and client_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Admin users must specify client_id"
        )
    
    assignments = db.query(DocumentAssignment).options(
        joinedload(DocumentAssignment.document)
    ).filter(
        DocumentAssignment.client_id == client_id,
        DocumentAssignment.is_active == True
    ).all()
    
    return assignments

@router.get("/tasks", response_model=List[TaskResponse])
async def get_client_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Get tasks for the current user's client"""
    client_id = current_user.client_id
    if current_user.is_admin and client_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Admin users must specify client_id"
        )
    
    tasks = db.query(Task).filter(
        Task.client_id == client_id,
        Task.is_active == True
    ).order_by(Task.due_date.asc(), Task.priority.desc()).all()
    
    return tasks

@router.post("/inquiries", response_model=ClientInquiryResponse)
async def submit_inquiry(
    inquiry_data: ClientInquiryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Submit a new HR inquiry"""
    client_id = current_user.client_id
    if current_user.is_admin and client_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Admin users must specify client_id"
        )
    
    db_inquiry = ClientInquiry(
        **inquiry_data.dict(),
        client_id=client_id,
        submitted_by_id=current_user.id
    )
    
    db.add(db_inquiry)
    db.commit()
    db.refresh(db_inquiry)
    return db_inquiry

@router.get("/inquiries", response_model=List[ClientInquiryResponse])
async def get_client_inquiries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Get inquiries submitted by the current user's client"""
    client_id = current_user.client_id
    if current_user.is_admin and client_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Admin users must specify client_id"
        )
    
    inquiries = db.query(ClientInquiry).filter(
        ClientInquiry.client_id == client_id
    ).order_by(ClientInquiry.created_at.desc()).all()
    
    return inquiries

@router.get("/inquiries/{inquiry_id}", response_model=ClientInquiryResponse)
async def get_inquiry_detail(
    inquiry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Get specific inquiry details"""
    inquiry = db.query(ClientInquiry).filter(
        ClientInquiry.id == inquiry_id
    ).first()
    
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    # Check if user has access to this inquiry
    if not current_user.is_admin and inquiry.client_id != current_user.client_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return inquiry

@router.get("/dashboard/summary")
async def get_client_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_client_user)
):
    """Get dashboard summary for client"""
    client_id = current_user.client_id
    if current_user.is_admin and client_id is None:
        raise HTTPException(
            status_code=400, 
            detail="Admin users must specify client_id"
        )
    
    # Count assigned documents
    document_count = db.query(DocumentAssignment).filter(
        DocumentAssignment.client_id == client_id,
        DocumentAssignment.is_active == True
    ).count()
    
    # Count pending tasks
    pending_tasks = db.query(Task).filter(
        Task.client_id == client_id,
        Task.status.in_(["pending", "in_progress"]),
        Task.is_active == True
    ).count()
    
    # Count open inquiries
    open_inquiries = db.query(ClientInquiry).filter(
        ClientInquiry.client_id == client_id,
        ClientInquiry.status.in_(["open", "in_review"])
    ).count()
    
    # Get upcoming tasks (next 7 days)
    from datetime import datetime, timedelta
    next_week = datetime.utcnow() + timedelta(days=7)
    upcoming_tasks = db.query(Task).filter(
        Task.client_id == client_id,
        Task.due_date <= next_week,
        Task.due_date >= datetime.utcnow(),
        Task.status.in_(["pending", "in_progress"]),
        Task.is_active == True
    ).order_by(Task.due_date.asc()).limit(5).all()
    
    return {
        "document_count": document_count,
        "pending_tasks": pending_tasks,
        "open_inquiries": open_inquiries,
        "upcoming_tasks": [
            {
                "id": task.id,
                "title": task.title,
                "due_date": task.due_date,
                "priority": task.priority.value
            } for task in upcoming_tasks
        ]
    }