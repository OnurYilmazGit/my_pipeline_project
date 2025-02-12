from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Create a synchronous SQLAlchemy engine using the database URL from settings
engine = create_engine(settings.database_url, echo=False, future=True)

# Configure a sessionmaker, which will serve as a factory for new Session objects
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """
    Dependency for FastAPI routes to retrieve a DB session.
    """
    db = SessionLocal()  # Create a new database session
    try:
        yield db  # Provide the session to the caller
    finally:
        db.close()  # Ensure the session is closed after use
