from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base

class TaskStatus(enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(enum.Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(Base):
    """Compliance tasks and internal notes model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(100), nullable=False)  # compliance_audit, training, note, etc.
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f"<Task(title='{self.title}', status='{self.status.value}', client_id={self.client_id})>"

class ClientInquiry(Base):
    """Client-submitted HR questions and incidents"""
    __tablename__ = "client_inquiries"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    inquiry_type = Column(String(100), nullable=False)  # question, incident, complaint, etc.
    status = Column(String(50), default="open")  # open, in_review, resolved, closed
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Response and resolution
    admin_response = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="inquiries")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    
    def __repr__(self):
        return f"<ClientInquiry(subject='{self.subject}', status='{self.status}', client_id={self.client_id})>"