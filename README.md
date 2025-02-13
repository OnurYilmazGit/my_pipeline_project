# My Pipeline Project

This repository provides a **FastAPI** web application that launches an **asynchronous** Celery pipeline to transform an integer input in three steps, storing partial or final results in a **PostgreSQL** database, with **Redis** as the message broker. The pipeline performs the following tasks:
- **Step A:** Pull data from an external API.
- **Step B:** Store the external result in the database and generate a UUID.
- **Step C:** Retrieve the stored data using that UUID and return the final JSON.

---

## Table of Contents

1. [Overview & Features](#1-overview--features)
2. [How It Meets the Assignment Requirements](#2-how-it-meets-the-assignment-requirements)
3. [Project Structure](#3-project-structure)
4. [Setup & Quickstart](#4-setup--quickstart)
5. [Usage](#5-usage)
6. [Testing](#6-testing)
7. [Versioning & Migrations](#7-versioning--migrations)
8. [Technical Details](#8-technical-details)
9. [Future Improvements](#9-future-improvements)
10. [Conclusion](#10-conclusion)

---

## 1. **Overview & Features**

1. **FastAPI** app with two main endpoints:
   - `POST /pipeline`: Creates a new pipeline job in the DB, triggers Celery tasks.
   - `GET /pipeline/{job_id}`: Retrieves the current status and partial/final results.
2. **Celery** tasks chained together:
   - **Step A:** `step_pull_external_api` pulls data from an external API.
   - **Step B:** `step_store_data` stores the fetched data in the DB and generates a new UUID.
   - **Step C:** `step_final_retrieve` retrieves the stored data using that UUID and finalizes the job.
3. **PostgreSQL** database storing:
   - Job ID (`UUID`)
   - Job status (`pending`, `in_progress`, `completed`, `error`)
   - Partial/final results (JSON)
   - Creation/update timestamps
4. **Redis** broker for task queueing.
5. **Docker Compose** setup for easy local deployment.
6. **Tests** (Pytest) verifying end-to-end functionality.
7. **(Optional)** A minimal React or similar frontend to visually demonstrate pipeline creation/polling.

---

## 2. **How It Meets the Assignment Requirements**

1. **FastAPI Endpoints**
   - `POST /pipeline`: Returns a new `job_id`, sets status to `in_progress`, and triggers the Celery pipeline.
   - `GET /pipeline/{job_id}`: Returns JSON with the current status and partial/final results.
2. **Celery Configuration & Chaining**
   - `celery_app.py` is configured with a Redis broker.
   - The `pipeline_orchestrator` chains the following tasks:
     1. `step_pull_external_api` – fetches data from an external API.
     2. `step_store_data` – stores the external data in the DB and generates a UUID.
     3. `step_final_retrieve` – retrieves data by the UUID and finalizes the job.
3. **Database Integration**
   - A single table (`pipeline_jobs`) is used, with columns for job ID, status, result (JSON), and timestamps.
   - SQLAlchemy models and CRUD operations manage the database interactions.
4. **Task Flow & Status Updates**
   - Upon `POST /pipeline`, a job is created and marked as `in_progress`.
   - Each task updates the DB record with partial data or the final result.
   - On success, the job status becomes `completed`; on error, it is marked `error`.
5. **Deploy / Docker**
   - `docker-compose.yml` sets up the FastAPI app, Celery worker, Redis broker, and PostgreSQL DB.
   - Healthchecks ensure that the DB is ready before the FastAPI app starts.
6. **Tests**
   - A Pytest suite validates the pipeline by making a POST request, polling the GET endpoint, and verifying the final output.
7. **Code Clarity & Pythonic Style**
   - The project is organized into logical modules (e.g., `app/models.py`, `app/tasks.py`, `app/routers/`).
   - Logging is implemented in tasks, and type hints are used throughout.
   - Environment-based configuration is supported via a `.env` file.

---

## 3. **Project Structure**

```
my_pipeline_project/
├── .env.example          # Example environment variables
├── docker-compose.yml    # Defines services: web, worker, db, redis
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
│   ├── config.py         # Environment-based configuration
│   ├── celery_app.py     # Celery instance configuration
│   ├── tasks.py          # Celery task functions
│   ├── crud.py           # Database CRUD helpers
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

2. **Copy** `.env.example` to `.env` and update values:

   ```bash
   cp .env.example .env
   # Edit .env to set POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, etc.
   ```

3. **Run** with Docker Compose:

   ```bash
   docker-compose up --build
   ```

4. **Verify**:
   - FastAPI runs on [http://localhost:8000](http://localhost:8000)
   - API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. **Usage**

1. **POST** `/pipeline`:

   ```bash
   curl -X POST -H "Content-Type: application/json" \
        -d '{"initial_value": 10}' \
        http://localhost:8000/pipeline
   ```
   This returns a JSON response with a `job_id` and a status of "in_progress".

2. **GET** `/pipeline/{job_id}`:

   ```bash
   curl http://localhost:8000/pipeline/<JOB_ID>
   ```
   This returns the current status (e.g., "pending", "in_progress", "completed", or "error") and any partial or final results in JSON format.

---

## 6. **Testing**

- **Integration Tests** are located in `tests/test_pipeline.py`.
- Run tests inside Docker (recommended):

  ```bash
  docker-compose run --rm web pytest
  ```
  Expected output:

  ```text
  collected 4 items
  tests/test_pipeline.py ....
  4 passed in X.XXs
  ```

- Locally, if you adjust the DB host accordingly:

  ```bash
  pip install -r requirements.txt
  pytest
  ```

---

## 7. **Versioning & Migrations**

- **Current Version**: `v1.0.0`
- This project uses `Base.metadata.create_all(bind=engine)` to create the database schema. For production, consider integrating Alembic for managing migrations.

---

## 8. **Technical Details**

- **Language & Framework**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15
- **Broker**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Celery 5.3
- **Testing**: Pytest 7
- **Docker**: Multi-service environment managed via `docker-compose`
- **External API**: For demonstration, data is pulled from [https://jsonplaceholder.typicode.com/todos/{initial_value}](https://jsonplaceholder.typicode.com/todos/{initial_value})

---

## 9. **Future Improvements**

- **Enhanced Logging**: Use `logging.config.dictConfig` for more structured logging.
- **Retry Logic**: Utilize Celery's `autoretry_for` for transient failures, such as external API timeouts.
- **Auth & Security**: Add OAuth2 or API keys if needed.
- **Async Database Access**: Consider using an async ORM (like SQLAlchemy with asyncio) if a fully asynchronous architecture is desired.
- **Kubernetes**: Provide Helm charts or Kubernetes manifests for production deployment.

---

## 10. **Conclusion**

This project fulfills the core **Take-Home Assignment** requirements:

- **Two endpoints** (`POST /pipeline` and `GET /pipeline/{job_id}`).
- **Chained Celery tasks** that pull external data, store it with a new UUID, and finalize the job.
- **PostgreSQL** for partial/final result storage.
- **Docker** for easy deployment.
- **Pytest suite** verifying the end-to-end pipeline functionality.

Feel free to fork, modify, or extend with additional features. Feedback and contributions are welcome!

---

### **Final Comments**

- Make sure the version numbers in the Table of Contents and section headers match (I updated them above).
- Verify that your external API endpoint in the tasks (JSONPlaceholder) is correctly referenced in both your code and README.
- If you have an optional frontend, you can add a brief section about it; otherwise, it's fine as is.

Overall, your README is clear, professional, and well-organized. With these minor adjustments, it should be excellent for developers to understand and use your project.

