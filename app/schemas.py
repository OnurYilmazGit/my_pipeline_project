from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID

class PipelineCreate(BaseModel):
    """
    Schema for creating a new pipeline job.
    """
    initial_value: int  # The initial integer value to start the pipeline process

class PipelineStatus(BaseModel):
    """
    Schema for representing the status and result of a pipeline job.
    """
    job_id: UUID  # Unique identifier for the pipeline job
    status: str  # Current status of the job (e.g., pending, in_progress, completed, error)
    result: Optional[Any] = None  # Result of the job, can be partial or final, or None if not yet available
