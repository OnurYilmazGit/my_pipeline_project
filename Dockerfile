# Dockerfile
FROM python:3.11-slim as base

# Create a working directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements or pyproject.toml
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI code
COPY app/ ./app/

# Copy your tests folder
COPY tests/ ./tests/

# Expose port 8000
EXPOSE 8000

# By default, run FastAPI using uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
