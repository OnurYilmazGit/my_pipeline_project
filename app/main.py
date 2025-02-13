import logging
from fastapi import FastAPI
from app.config import settings
from app.models import Base
from app.database import engine
from app.routers import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.include_router(pipeline.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to My Pipeline Project"}
