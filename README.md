# My Pipeline Project

This repository provides a **FastAPI** web application that launches an **asynchronous** Celery pipeline to transform an integer input in three steps, storing partial or final results in a **PostgreSQL** database, with **Redis** as the message broker.

---

## 1. **Overview & Features**

1. **FastAPI** app with two main endpoints:
   - `POST /pipeline`: Creates a new pipeline job in the DB, triggers Celery tasks.
   - `GET /pipeline/{job_id}`: Retrieves the current status and partial/final results.
2. **Celery** tasks chained together (e.g., “add 5,” “multiply by 2,” “subtract 10”).
3. **PostgreSQL** database storing:
   - Job ID (`UUID`)
   - Job status (`pending`, `in_progress`, `completed`, `error`)
   - Partial/final results (JSON)
   - Creation/update timestamps
4. **Redis** broker for task queueing.
5. **Docker Compose** setup for easy local deployment:
   - `fastapi_app` (web server)
   - `celery_worker` (background worker)
   - `postgres_db` (database)
   - `redis_broker` (broker)
6. **Tests** (Pytest) verifying end-to-end functionality.  
7. **(Optional)** A minimal React or similar frontend to visually demonstrate pipeline creation/polling.

---

## 2. **How It Meets the Assignment Requirements**

1. **FastAPI Endpoints**  
   - `POST /pipeline`: Returns a new `job_id`, sets status to `in_progress`, and calls Celery.  
   - `GET /pipeline/{job_id}`: Returns JSON with status and partial/final result.

2. **Celery Configuration & Chaining**  
   - We have a `celery_app.py` referencing a Redis broker.  
   - `pipeline_orchestrator` chain: 
     1. `step_add_5`
     2. `step_multiply_2`
     3. `step_subtract_10`

3. **Database Integration**  
   - Single table (`pipeline_jobs`) with columns: `job_id`, `status`, `result (JSON)`, timestamps.  
   - SQLAlchemy models and CRUD operations (`create_pipeline_job`, `update_pipeline_job`, etc.).

4. **Task Flow & Status Updates**  
   - On `POST /pipeline`, we insert a “job” record, set `status="in_progress"`.  
   - Each Celery task updates the DB record with partial or final results, or `error` on exception.

5. **Deploy / Docker**  
   - `docker-compose.yml` spins up everything:  
     - FastAPI app (`web` service)  
     - Celery worker (`worker` service)  
     - Redis broker  
     - PostgreSQL DB  
   - **Healthcheck** for Postgres ensures the app only starts once the DB is ready.

6. **Tests**  
   - Pytest suite that calls `POST /pipeline`, polls `GET /pipeline/{job_id}`, and verifies final outcome.  
   - Parametrized for multiple inputs.

7. **Code Clarity & Pythonic Style**  
   - Well-organized structure: `app/` folder with `models.py`, `tasks.py`, `routers/`, etc.  
   - Logging in tasks, typed function signatures, environment-based config.

---

## 3. **Project Structure**

```
my_pipeline_project/
├── .env.example          # Example environment variables
├── docker-compose.yml    # Defines web, worker, db, redis
├── Dockerfile            # FastAPI container
├── Dockerfile.worker     # Celery worker container
├── requirements.txt      # Python dependencies
├── README.md             # (This document)
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI entrypoint
│   ├── models.py         # SQLAlchemy models
│   ├── schemas.py        # Pydantic models
│   ├── database.py       # DB engine and session
│   ├── config.py         # Env-based configuration
│   ├── celery_app.py     # Celery instance
│   ├── tasks.py          # Task functions
│   ├── crud.py           # DB create/update/retrieve helpers
│   └── routers/
│       └── pipeline.py   # /pipeline endpoints
└── tests/
    ├── __init__.py
    └── test_pipeline.py  # Pytest integration tests
```

---

## 4. **Setup & Quickstart**

1. **Clone** the repository:

   ```bash
   git clone https://github.com/yourusername/my_pipeline_project.git
   cd my_pipeline_project
   ```

2. **Copy** `.env.example` to `.env` and fill in your environment variables:

   ```bash
   cp .env.example .env
   # Update POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, etc.
   ```

3. **Run** with Docker Compose:

   ```bash
   docker-compose up --build
   ```

4. **Verify**:
   - FastAPI runs on [http://localhost:8000](http://localhost:8000)  
   - API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. **Usage**

1. **POST** `/pipeline`:

   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"initial_value": 10}' \
        http://localhost:8000/pipeline
   ```
   Returns a JSON with `job_id` and `status`.

2. **GET** `/pipeline/{job_id}`:

   ```bash
   curl http://localhost:8000/pipeline/<JOB_ID>
   ```
   Returns current status:
   - `"pending"`, `"in_progress"`, `"completed"`, or `"error"`  
   - `result` can be partial or final JSON.

---

## 6. **Testing**

- **Integration Tests** are in `tests/test_pipeline.py`.  
- Run **in Docker** (preferred) so the `db` hostname resolves:

  ```bash
  docker-compose run --rm web pytest
  ```
  You’ll see:

  ```text
  collected 1 item
  tests/test_pipeline.py .
  1 passed in 2.34s
  ```

- **Locally** (not recommended unless you change DB host to `localhost` in `.env`):

  ```bash
  pip install -r requirements.txt
  pytest
  ```

---

## 7. **Frontend (Optional)**

You can add a minimal **React** (or other) frontend that calls `/pipeline` and displays job status. If you do:

- Create a `frontend/` folder with a `Dockerfile.frontend`.  
- Update `docker-compose.yml` to include a `frontend` service.  
- The user can then visit [http://localhost:3000](http://localhost:3000) to create pipeline jobs and see real-time status updates.

---

## 8. **Versioning & Migrations**

- **Current Version**: `v1.0.0`  
- **Migrations**: This project uses `Base.metadata.create_all(bind=engine)` for schema creation. In production, you could integrate [**Alembic**](https://alembic.sqlalchemy.org/) for versioned migrations.

---

## 9. **Technical Details**

- **Language & Framework**: Python 3.11, FastAPI  
- **Database**: PostgreSQL 15  
- **Broker**: Redis 7  
- **ORM**: SQLAlchemy 2.0  
- **Task Queue**: Celery 5.3  
- **Testing**: Pytest 7  
- **Docker**: Multi-service environment via `docker-compose`.

---

## 10. **Future Improvements**

- **Enhanced Logging**: Use [logging.config.dictConfig](https://docs.python.org/3/library/logging.config.html) for more structured logs.  
- **Retry Logic**: Celery’s `autoretry_for` for transient failures (e.g., external API calls).  
- **Auth & Security**: Add OAuth2 or API keys if needed in production.  
- **Async DB**: Use `async SQLAlchemy` if fully async is desired.  
- **Kubernetes**: Provide Helm charts or K8s manifests for production scaling.

---

## **Conclusion**

This project fulfills the core **Take-Home Assignment** requirements:

- **Two endpoints** (`POST /pipeline`, `GET /pipeline/{job_id}`)  
- **Chained Celery tasks** passing data and updating DB.  
- **PostgreSQL** for partial/final result storage.  
- **Docker** for easy deployment.  
- **Pytest suite** verifying functionality end-to-end.

Feel free to fork, modify, or extend with additional features like advanced logging, authentication, or a more polished frontend. Feedback and contributions are welcome!

---

