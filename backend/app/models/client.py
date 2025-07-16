from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Client(Base):
    """Client company model"""
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    industry = Column(String(100), nullable=False)  # healthcare, construction, professional services
    employee_count = Column(Integer, nullable=False)
    point_of_contact = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # Internal admin notes
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="client")
    documents = relationship("DocumentAssignment", back_populates="client")
    tasks = relationship("Task", back_populates="client")
    inquiries = relationship("ClientInquiry", back_populates="client")
    
    def __repr__(self):
        return f"<Client(company_name='{self.company_name}', industry='{self.industry}')>"