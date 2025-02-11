from sqlalchemy.orm import Session
from uuid import UUID
from app.models import PipelineJob

def create_pipeline_job(db: Session) -> PipelineJob:
    new_job = PipelineJob(status="pending")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

def update_pipeline_job(db: Session, job_id: UUID, **kwargs) -> PipelineJob:
    job = db.query(PipelineJob).filter(PipelineJob.job_id == job_id).one_or_none()
    if not job:
        return None
    for k, v in kwargs.items():
        setattr(job, k, v)
    db.commit()
    db.refresh(job)
    return job

def get_pipeline_job(db: Session, job_id: UUID) -> PipelineJob:
    return db.query(PipelineJob).filter(PipelineJob.job_id == job_id).one_or_none()
