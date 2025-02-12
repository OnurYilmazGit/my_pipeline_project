from sqlalchemy.orm import Session
from uuid import UUID
from app.models import PipelineJob

def create_pipeline_job(db: Session) -> PipelineJob:
    """
    Create a new pipeline job with a default status of 'pending'.
    """
    new_job = PipelineJob(status="pending")
    db.add(new_job)  # Add the new job to the session
    db.commit()  # Commit the transaction to save the job in the database
    db.refresh(new_job)  # Refresh the instance to reflect the database state
    return new_job

def update_pipeline_job(db: Session, job_id: UUID, **kwargs) -> PipelineJob:
    """
    Update an existing pipeline job with new values.
    """
    job = db.query(PipelineJob).filter(PipelineJob.job_id == job_id).one_or_none()
    if not job:
        return None  # Return None if the job does not exist
    for k, v in kwargs.items():
        setattr(job, k, v)  # Update the job attributes with provided values
    db.commit()  # Commit the changes to the database
    db.refresh(job)  # Refresh the instance to reflect the updated state
    return job

def get_pipeline_job(db: Session, job_id: UUID) -> PipelineJob:
    """
    Retrieve a pipeline job by its job_id.
    """
    return db.query(PipelineJob).filter(PipelineJob.job_id == job_id).one_or_none()  # Return the job or None if not found
