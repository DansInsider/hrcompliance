from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_admin: bool = False
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    client_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    client_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Client schemas
class ClientBase(BaseModel):
    company_name: str
    industry: str
    employee_count: int
    point_of_contact: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    point_of_contact: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class ClientResponse(ClientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Document schemas
class DocumentBase(BaseModel):
    original_filename: str
    description: Optional[str] = None
    document_type: str

class DocumentCreate(DocumentBase):
    filename: str
    file_path: str
    file_size: int
    mime_type: str
    uploaded_by_id: int

class DocumentResponse(DocumentBase):
    id: int
    filename: str
    file_size: int
    mime_type: str
    uploaded_by_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Document assignment schemas
class DocumentAssignmentCreate(BaseModel):
    document_id: int
    client_id: int
    notes: Optional[str] = None

class DocumentAssignmentResponse(BaseModel):
    id: int
    document_id: int
    client_id: int
    assigned_by_id: int
    assigned_at: datetime
    notes: Optional[str] = None
    document: DocumentResponse
    
    class Config:
        from_attributes = True

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    client_id: int
    assigned_to_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[datetime] = None
    assigned_to_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    client_id: int
    created_by_id: int
    assigned_to_id: Optional[int] = None
    completed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Client inquiry schemas
class ClientInquiryBase(BaseModel):
    subject: str
    description: str
    inquiry_type: str
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM

class ClientInquiryCreate(ClientInquiryBase):
    pass

class ClientInquiryResponse(ClientInquiryBase):
    id: int
    client_id: int
    submitted_by_id: int
    status: str
    assigned_to_id: Optional[int] = None
    admin_response: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str