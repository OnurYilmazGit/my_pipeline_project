from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app import crud
from app.schemas import PipelineCreate, PipelineStatus
from app.tasks import pipeline_orchestrator

router = APIRouter()

@router.post("/pipeline", response_model=PipelineStatus)
def create_pipeline(payload: PipelineCreate, db: Session = Depends(get_db)):
    """
    1. Create a pipeline job in DB with status='pending'.
    2. Immediately update status to 'in_progress'.
    3. Launch the Celery orchestrator task (pipeline_orchestrator).
    4. Return job_id for tracking.
    """
    # Create a new DB record
    job = crud.create_pipeline_job(db)
    
    # Update status to 'in_progress'
    updated_job = crud.update_pipeline_job(db, job.job_id, status="in_progress")

    # Kick off the Celery orchestrator asynchronously
    pipeline_orchestrator.delay(payload.initial_value, str(updated_job.job_id))

    return PipelineStatus(
        job_id=updated_job.job_id,
        status=updated_job.status,
        result=updated_job.result
    )

@router.get("/pipeline/{job_id}", response_model=PipelineStatus)
def get_pipeline_status(job_id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve the current status and result for a pipeline job.
    """
    job = crud.get_pipeline_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return PipelineStatus(
        job_id=job.job_id,
        status=job.status,
        result=job.result
    )
