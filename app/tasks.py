import logging
import uuid
import requests
from celery import chain
from app.celery_app import celery_app
from app.database import SessionLocal
from app.crud import update_pipeline_job, get_pipeline_job

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def step_pull_external_api(self, input_val: int) -> dict:
    """
    Step A: Pull from an external API using the integer input.
    In this example, we call JSONPlaceholder's /todos/{id} endpoint.
    Returns the external data as a dictionary.
    """
    url = f"https://jsonplaceholder.typicode.com/todos/{input_val}"
    logger.info("Fetching external API from %s", url)

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        logger.info("External API data: %s", data)
        return data  # pass this to next step
    except Exception as e:
        logger.error("Error pulling external API: %s", e)
        raise e

@celery_app.task(bind=True)
def step_store_data(self, external_data: dict, job_id: str) -> str:
    """
    Step B: Generate a new UUID, store the external data in DB under 'data_uuid'
    in the 'result' field, so we can retrieve it later.
    Returns the new UUID (as a string) for the next step.
    """
    new_uuid = str(uuid.uuid4())
    logger.info("Storing external_data under UUID=%s for job=%s", new_uuid, job_id)

    db = SessionLocal()
    try:
        update_pipeline_job(
            db,
            job_id,
            result={
                "data_uuid": new_uuid,
                "external_data": external_data
            }
        )
    finally:
        db.close()

    return new_uuid

@celery_app.task(bind=True)
def step_final_retrieve(self, data_uuid: str, job_id: str) -> dict:
    """
    Step C: Retrieve from DB by job_id, parse the 'data_uuid' & 'external_data',
    finalize job => status='completed', store final JSON.
    """
    logger.info("Final retrieve for job=%s, data_uuid=%s", job_id, data_uuid)

    db = SessionLocal()
    try:
        job_record = get_pipeline_job(db, job_id)
        if not job_record or not job_record.result:
            raise ValueError("No result stored for this job yet")

        # The external data we stored in step B:
        ext_data = job_record.result.get("external_data")
        # For demonstration, let's do a "final" transform or just store it as is
        final_data = {
            "final_data": ext_data,
            "uuid": data_uuid
        }

        update_pipeline_job(
            db,
            job_id,
            status="completed",
            result=final_data
        )

        return final_data
    finally:
        db.close()

@celery_app.task(bind=True)
def pipeline_orchestrator(self, initial_value: int, job_id: str):
    """
    Orchestrates the chain of tasks:
      1) step_pull_external_api
      2) step_store_data
      3) step_final_retrieve
    """
    try:
        workflow = chain(
            step_pull_external_api.s(initial_value),
            step_store_data.s(job_id),
            step_final_retrieve.s(job_id)
        )
        workflow.apply_async()
    except Exception as e:
        logger.error("Pipeline orchestrator error: %s", str(e))
        db = SessionLocal()
        update_pipeline_job(db, job_id, status="error", result={"error": str(e)})
        db.close()
        raise e
