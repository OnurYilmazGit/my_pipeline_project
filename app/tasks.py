import logging
from uuid import UUID

from celery import chain
from app.celery_app import celery_app
from app.database import SessionLocal
from app.crud import update_pipeline_job

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def step_add_5(self, value: int) -> int:
    """
    Step A: Adds 5 to the input integer.
    """
    logger.info("Adding 5 to %d", value)
    return value + 5

@celery_app.task(bind=True)
def step_multiply_2(self, value: int, job_id: str) -> int:
    """
    Step B: Multiply the incoming value by 2, then store a partial result in DB.
    """
    result = value * 2
    logger.info("Multiplying result by 2: %d -> %d", value, result)

    # Save partial to DB
    db = SessionLocal()
    update_pipeline_job(db, job_id, result={"partial": result})
    db.close()

    return result

@celery_app.task(bind=True)
def step_subtract_10(self, value: int, job_id: str) -> dict:
    """
    Step C: Subtract 10, update the record status to 'completed', store final result.
    """
    final_value = value - 10
    logger.info("Subtracting 10: %d -> %d", value, final_value)

    db = SessionLocal()
    updated_job = update_pipeline_job(
        db, 
        job_id, 
        status="completed",
        result={"final_result": final_value}
    )
    db.close()

    return {"final_result": final_value, "job_id": str(job_id)}

@celery_app.task(bind=True)
def pipeline_orchestrator(self, initial_value: int, job_id: str):
    """
    Master Orchestrator Task:
    Kicks off a chain of tasks to process `initial_value`.
    If it fails immediately, mark job as 'error'.
    """
    try:
        # Create a task chain
        workflow = chain(
            step_add_5.s(initial_value),
            step_multiply_2.s(job_id),
            step_subtract_10.s(job_id)
        )
        # Launch the asynchronous workflow
        workflow.apply_async()
    except Exception as e:
        logger.error("Pipeline orchestrator error: %s", str(e))
        db = SessionLocal()
        update_pipeline_job(db, job_id, status="error", result={"error": str(e)})
        db.close()
        raise e
