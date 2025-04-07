from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

# Create database engine
# Check if DATABASE_URL is defined in settings
database_url = getattr(settings, "DATABASE_URL", None)

if not database_url:
    # Use SQLite as fallback for development/testing
    SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
    connect_args = {"check_same_thread": False}
else:
    # Use PostgreSQL for production
    SQLALCHEMY_DATABASE_URL = database_url
    connect_args = {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    **connect_args
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 