from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Document(Base):
    """Document storage model"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)  # User-friendly name
    file_path = Column(String(500), nullable=False)  # Server file path
    file_size = Column(Integer, nullable=False)  # File size in bytes
    mime_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    document_type = Column(String(100), nullable=False)  # handbook, training, checklist, etc.
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploaded_by = relationship("User")
    assignments = relationship("DocumentAssignment", back_populates="document")
    
    def __repr__(self):
        return f"<Document(filename='{self.original_filename}', type='{self.document_type}')>"

class DocumentAssignment(Base):
    """Many-to-many relationship between documents and clients"""
    __tablename__ = "document_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    assigned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)  # Assignment-specific notes
    is_active = Column(Boolean, default=True)
    
    # Relationships
    document = relationship("Document", back_populates="assignments")
    client = relationship("Client", back_populates="documents")
    assigned_by = relationship("User")
    
    def __repr__(self):
        return f"<DocumentAssignment(doc_id={self.document_id}, client_id={self.client_id})>"