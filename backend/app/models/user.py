from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    """User model for both admin and client users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key to client company (null for admin users)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    
    # Relationships
    client = relationship("Client", back_populates="users")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="created_by")
    
    def __repr__(self):
        return f"<User(email='{self.email}', is_admin={self.is_admin})>"