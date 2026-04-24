from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, LargeBinary, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class UserIdentity(Base):
    __tablename__ = "identities"

    id = Column(Integer, primary_key=True, index=True)
    national_id = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Encrypted Metadata
    metadata_blob = Column(LargeBinary, nullable=True) 

    # Relationships
    embeddings = relationship("Embedding", back_populates="identity")
    audit_logs = relationship("AuditLog", back_populates="identity")

class Embedding(Base):
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    identity_id = Column(Integer, ForeignKey("identities.id"))
    
    # Store reference to vector cluster ID, not the vector itself (security)
    vector_index_id = Column(Integer, nullable=False)
    
    # Hash of the vector for integrity checking
    vector_hash = Column(String, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    identity = relationship("UserIdentity", back_populates="embeddings")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False) # ENROLL, SEARCH, VERIFY
    identity_id = Column(Integer, ForeignKey("identities.id"), nullable=True)
    
    request_ip = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=True)
    status = Column(String, nullable=False) # SUCCESS, FAILURE, SUSPICIOUS
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    identity = relationship("UserIdentity", back_populates="audit_logs")
