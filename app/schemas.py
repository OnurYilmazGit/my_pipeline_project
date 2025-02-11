from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID

class PipelineCreate(BaseModel):
    initial_value: int

class PipelineStatus(BaseModel):
    job_id: UUID
    status: str
    result: Optional[Any] = None
