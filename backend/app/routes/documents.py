from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.schemas.models import DocumentResponse, DocumentCreate
from app.utils.auth import get_current_active_user, get_admin_user
from app.utils.file_handler import handle_file_upload, delete_file
import os

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    description: str = "",
    document_type: str = "general",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Upload a new document (admin only)"""
    try:
        # Handle file upload
        unique_filename, file_path, file_size = await handle_file_upload(file)
        
        # Create document record
        db_document = Document(
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            description=description,
            document_type=document_type,
            uploaded_by_id=current_user.id
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return db_document
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    document_type: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all documents with optional filtering (admin only)"""
    query = db.query(Document).filter(Document.is_active == True)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    documents = query.offset(skip).limit(limit).all()
    return documents

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get specific document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access permissions
    if not current_user.is_admin:
        # For client users, check if document is assigned to their client
        from app.models.document import DocumentAssignment
        assignment = db.query(DocumentAssignment).filter(
            DocumentAssignment.document_id == document_id,
            DocumentAssignment.client_id == current_user.client_id,
            DocumentAssignment.is_active == True
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return document

@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download document file"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check access permissions
    if not current_user.is_admin:
        # For client users, check if document is assigned to their client
        from app.models.document import DocumentAssignment
        assignment = db.query(DocumentAssignment).filter(
            DocumentAssignment.document_id == document_id,
            DocumentAssignment.client_id == current_user.client_id,
            DocumentAssignment.is_active == True
        ).first()
        
        if not assignment:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(document.file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=document.file_path,
        filename=document.original_filename,
        media_type=document.mime_type
    )

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete document (admin only)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Deactivate document record
    document.is_active = False
    
    # Deactivate all assignments
    from app.models.document import DocumentAssignment
    assignments = db.query(DocumentAssignment).filter(
        DocumentAssignment.document_id == document_id
    ).all()
    
    for assignment in assignments:
        assignment.is_active = False
    
    db.commit()
    
    # Optionally delete physical file
    delete_file(document.file_path)
    
    return {"message": "Document deleted successfully"}

@router.get("/types/list")
async def get_document_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get list of available document types"""
    # Get distinct document types from database
    types = db.query(Document.document_type).distinct().all()
    type_list = [t[0] for t in types]
    
    # Add common types if not present
    common_types = ["handbook", "training", "checklist", "policy", "form", "template"]
    for doc_type in common_types:
        if doc_type not in type_list:
            type_list.append(doc_type)
    
    return {"document_types": sorted(type_list)}