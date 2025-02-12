import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "My Pipeline Project"  # Name of the application
    APP_ENV: str = "development"  # Environment the app is running in (e.g., development, production)

    # Database configuration
    POSTGRES_DB: str = "mydb"  # Name of the PostgreSQL database
    POSTGRES_USER: str = "myuser"  # Username for the PostgreSQL database
    POSTGRES_PASSWORD: str = "mypassword"  # Password for the PostgreSQL database
    POSTGRES_HOST: str = "db"  # Host address for the PostgreSQL database
    POSTGRES_PORT: str = "5432"  # Port number for the PostgreSQL database

    # Celery broker configuration
    BROKER_URL: str = "redis://redis:6379/0"  # URL for the Redis broker used by Celery

    # Property to build the database URL for SQLAlchemy
    @property
    def database_url(self) -> str:
        # Constructs the database URL using the provided PostgreSQL settings
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        # Specifies the environment file to load variables from
        env_file = ".env"

# Instantiate the settings object
settings = Settings()
