import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "My Pipeline Project"
    APP_ENV: str = "development"

    POSTGRES_DB: str = "mydb"
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mypassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"

    # For a Celery broker (Redis in this example)
    BROKER_URL: str = "redis://localhost:6379/0"

    # Construct a SQLAlchemy-compatible DB URL
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"

settings = Settings()
