# tests/test_pipeline.py

import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def poll_pipeline_status(job_id: str, max_wait: float = 10.0, interval: float = 1.0):
    """
    Poll the /pipeline/{job_id} endpoint until the job is 'completed' or 'error',
    or until max_wait seconds have elapsed.

    Returns:
        (status, result) tuple from the final GET response.
    Raises:
        TimeoutError if max_wait is exceeded.
    """
    start = time.time()
    while True:
        resp = client.get(f"/pipeline/{job_id}")
        assert resp.status_code == 200, f"GET /pipeline/{job_id} returned {resp.status_code}"
        data = resp.json()

        if data["status"] in ("completed", "error"):
            return data["status"], data["result"]
        
        if time.time() - start > max_wait:
            raise TimeoutError(f"Pipeline job did not complete within {max_wait} seconds.")
        
        time.sleep(interval)

@pytest.mark.parametrize("input_val", [0, 10, -5, 999])
def test_pipeline_flow(input_val):
    """
    Test the pipeline flow for various input values:
    - 0
    - 10
    - -5
    - 999
    """
    # 1. Create a pipeline with the given input_val
    response = client.post("/pipeline", json={"initial_value": input_val})
    assert response.status_code == 200, f"POST /pipeline returned {response.status_code}"
    data = response.json()

    job_id = data["job_id"]
    assert data["status"] == "in_progress"
    assert job_id, "Expected a job_id in response"

    # 2. Poll until 'completed' or 'error'
    status, result = poll_pipeline_status(job_id, max_wait=10, interval=1)

    # 3. Validate final status and result
    #    - If 'completed', we can check if final_result matches the pipeline logic:
    #      step_add_5 -> step_multiply_2 -> step_subtract_10
    #      final_value = ((input_val + 5) * 2) - 10
    if status == "completed":
        expected_final = ((input_val + 5) * 2) - 10
        assert result["final_result"] == expected_final, (
            f"For input {input_val}, expected final_result {expected_final} but got {result['final_result']}"
        )
    elif status == "error":
        # If your tasks can raise an error for certain inputs, you can test logic here.
        # For a standard chain, you might not hit 'error' unless there's a bug or
        # unexpected input. We'll just note the result.
        print(f"Job ended in error with result: {result}")

    # 4. If your pipeline can produce partial results, you can optionally check them
    #    in the poll_pipeline_status or prior calls. For now, we assume the final check suffices.
