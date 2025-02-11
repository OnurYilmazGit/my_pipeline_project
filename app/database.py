from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Using a standard synchronous engine + session
engine = create_engine(settings.database_url, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """
    Dependency for FastAPI routes to retrieve a DB session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
