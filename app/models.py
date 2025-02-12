from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

# Base class for all models
Base = declarative_base()

class PipelineJob(Base):
    # Name of the table in the database
    __tablename__ = "pipeline_jobs"

    # Unique identifier for each job, using UUID
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Status of the job, default is 'pending'
    status = Column(String, nullable=False, default="pending")
    
    # JSON field to store the result of the job
    result = Column(JSON, nullable=True)
    
    # Timestamp for when the job was created, defaults to current time
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamp for when the job was last updated, automatically updated
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
