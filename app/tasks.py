import logging
from uuid import UUID

from celery import chain
from app.celery_app import celery_app
from app.database import SessionLocal
from app.crud import update_pipeline_job

# Set up logging for the tasks
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

    # Save partial result to the database
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

    # Update job status and store final result in the database
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
    If an error occurs immediately, mark job as 'error'.
    Otherwise chain the tasks step_add_5, step_multiply_2, step_subtract_10.
    """
    try:
        # Chain tasks to execute them sequentially
        workflow = chain(
            step_add_5.s(initial_value),
            step_multiply_2.s(job_id),
            step_subtract_10.s(job_id)
        )
        workflow.apply_async()
    except Exception as e:
        logger.error("Pipeline orchestrator error: %s", str(e))
        # Update job status to 'error' in case of failure
        db = SessionLocal()
        update_pipeline_job(db, job_id, status="error", result={"error": str(e)})
        db.close()
        raise e
