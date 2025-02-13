import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def poll_pipeline_status(job_id: str, max_wait: float = 15.0, interval: float = 1.0):
    """
    Poll the /pipeline/{job_id} endpoint until status in ('completed','error')
    or until max_wait is reached. Returns (status, result).
    """
    start = time.time()
    while True:
        resp = client.get(f"/pipeline/{job_id}")
        assert resp.status_code == 200, f"GET /pipeline/{job_id} -> {resp.status_code}"
        data = resp.json()
        if data["status"] in ("completed", "error"):
            return data["status"], data["result"]
        if time.time() - start > max_wait:
            raise TimeoutError("Pipeline didn't complete in time.")
        time.sleep(interval)

@pytest.mark.parametrize("input_val", [1, 2, 3])  # test with a few 'todos/{id}'
def test_pipeline_end_to_end(input_val):
    # 1. Trigger pipeline
    resp = client.post("/pipeline", json={"initial_value": input_val})
    assert resp.status_code == 200
    job_data = resp.json()
    job_id = job_data["job_id"]
    assert job_data["status"] == "in_progress"

    # 2. Poll until completed or error
    final_status, final_result = poll_pipeline_status(job_id, max_wait=20)
    if final_status == "completed":
        # Check final data structure
        assert "final_data" in final_result, "Expected 'final_data' in final result"
        ext_data = final_result["final_data"]
        # JSONPlaceholder /todos/{input_val} => 'id': input_val
        # Let's check that the retrieved external data has matching 'id'
        assert ext_data["id"] == input_val, f"Expected external 'id'={input_val}, got {ext_data['id']}"
        print(f"Job {job_id} completed successfully with final_data: {ext_data}")
    elif final_status == "error":
        print(f"Job {job_id} ended in error: {final_result}")
        pytest.fail("Pipeline ended with status=error unexpectedly.")
