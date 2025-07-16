from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.user import User
from app.models.client import Client
from app.models.document import Document, DocumentAssignment
from app.models.task import Task, ClientInquiry
from app.schemas.models import (
    ClientCreate, ClientUpdate, ClientResponse,
    TaskCreate, TaskUpdate, TaskResponse,
    DocumentAssignmentCreate, DocumentAssignmentResponse,
    UserCreate, UserResponse
)
from app.utils.auth import get_admin_user, get_password_hash

router = APIRouter(prefix="/admin", tags=["admin"])

# Client Management
@router.post("/clients", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new client company"""
    db_client = Client(**client_data.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/clients", response_model=List[ClientResponse])
async def get_clients(
    skip: int = 0,
    limit: int = 100,
    industry: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all clients with optional filtering"""
    query = db.query(Client).filter(Client.is_active == True)
    
    if industry:
        query = query.filter(Client.industry == industry)
    
    clients = query.offset(skip).limit(limit).all()
    return clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get specific client by ID"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update client information"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    db.commit()
    db.refresh(client)
    return client

@router.delete("/clients/{client_id}")
async def deactivate_client(
    client_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deactivate client (soft delete)"""
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    client.is_active = False
    db.commit()
    return {"message": "Client deactivated successfully"}

# User Management
@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate client_id if provided
    if user_data.client_id:
        client = db.query(Client).filter(Client.id == user_data.client_id).first()
        if not client:
            raise HTTPException(status_code=400, detail="Client not found")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_admin=user_data.is_admin,
        client_id=user_data.client_id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all users with optional client filtering"""
    query = db.query(User).filter(User.is_active == True)
    
    if client_id:
        query = query.filter(User.client_id == client_id)
    
    users = query.offset(skip).limit(limit).all()
    return users

# Document Assignment
@router.post("/documents/assign", response_model=DocumentAssignmentResponse)
async def assign_document_to_client(
    assignment_data: DocumentAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Assign a document to a client"""
    # Validate document exists
    document = db.query(Document).filter(Document.id == assignment_data.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Validate client exists
    client = db.query(Client).filter(Client.id == assignment_data.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Check if assignment already exists
    existing_assignment = db.query(DocumentAssignment).filter(
        DocumentAssignment.document_id == assignment_data.document_id,
        DocumentAssignment.client_id == assignment_data.client_id,
        DocumentAssignment.is_active == True
    ).first()
    
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Document already assigned to this client")
    
    # Create assignment
    db_assignment = DocumentAssignment(
        document_id=assignment_data.document_id,
        client_id=assignment_data.client_id,
        assigned_by_id=current_user.id,
        notes=assignment_data.notes
    )
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    # Load related data
    db_assignment = db.query(DocumentAssignment).options(
        joinedload(DocumentAssignment.document)
    ).filter(DocumentAssignment.id == db_assignment.id).first()
    
    return db_assignment

@router.get("/documents/assignments", response_model=List[DocumentAssignmentResponse])
async def get_document_assignments(
    client_id: Optional[int] = None,
    document_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get document assignments with optional filtering"""
    query = db.query(DocumentAssignment).options(
        joinedload(DocumentAssignment.document)
    ).filter(DocumentAssignment.is_active == True)
    
    if client_id:
        query = query.filter(DocumentAssignment.client_id == client_id)
    if document_id:
        query = query.filter(DocumentAssignment.document_id == document_id)
    
    assignments = query.offset(skip).limit(limit).all()
    return assignments

# Task Management
@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new compliance task"""
    db_task = Task(
        **task_data.dict(),
        created_by_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get tasks with optional filtering"""
    query = db.query(Task).filter(Task.is_active == True)
    
    if client_id:
        query = query.filter(Task.client_id == client_id)
    if status:
        query = query.filter(Task.status == status)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

# Client Inquiries Management
@router.get("/inquiries", response_model=List)
async def get_client_inquiries(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get client inquiries with optional filtering"""
    query = db.query(ClientInquiry)
    
    if client_id:
        query = query.filter(ClientInquiry.client_id == client_id)
    if status:
        query = query.filter(ClientInquiry.status == status)
    
    inquiries = query.offset(skip).limit(limit).all()
    return inquiries

@router.put("/inquiries/{inquiry_id}/respond")
async def respond_to_inquiry(
    inquiry_id: int,
    response_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Respond to client inquiry"""
    inquiry = db.query(ClientInquiry).filter(ClientInquiry.id == inquiry_id).first()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    
    inquiry.admin_response = response_data.get("response")
    inquiry.status = response_data.get("status", "in_review")
    inquiry.assigned_to_id = current_user.id
    
    db.commit()
    db.refresh(inquiry)
    return inquiry