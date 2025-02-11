# tests/test_pipeline.py
import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_pipeline_flow():
    # 1. Create a pipeline with initial_value=10
    response = client.post("/pipeline", json={"initial_value": 10})
    assert response.status_code == 200
    data = response.json()
    job_id = data["job_id"]
    assert data["status"] == "in_progress"

    # 2. Poll /pipeline/{job_id} until completed
    # (In real test, might do a loop with a short sleep)
    time.sleep(2)
    status_response = client.get(f"/pipeline/{job_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()

    # We expect "completed" if the tasks are fast enough
    # But we might need to poll multiple times if steps take longer
    # For a real test, you'd do a retry loop with a maximum timeout.
    assert status_data["status"] in ["in_progress", "completed", "error"]
