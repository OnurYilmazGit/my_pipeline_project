# My Pipeline Project

This project demonstrates a FastAPI application that triggers a Celery workflow
consisting of multiple chained tasks, storing partial/final results in a database.

## Requirements
- Docker and docker-compose
- Python 3.11+ (if running locally without Docker)

## Quickstart
1. Copy `.env.example` to `.env` and adjust as necessary.
2. Run `docker-compose up --build`.
3. Go to `http://localhost:8000/docs` to see the OpenAPI docs.

## Usage
- **POST** `/pipeline`: Starts a pipeline.
  ```bash
  curl -X POST http://localhost:8000/pipeline \
       -H "Content-Type: application/json" \
       -d '{"initial_value": 10}'
