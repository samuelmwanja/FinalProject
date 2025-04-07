import sys
import os
import logging

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import Base, engine
from app.models.user import User
from app.models.comment import Comment
from app.models.settings import MLSettings
from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database tables"""
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    settings = get_settings()
    logger.info("Database initialization starting...")
    
    if not settings.DATABASE_URL:
        logger.error("DATABASE_URL is not set in environment variables or .env file.")
        logger.info("Using SQLite as fallback.")
    
    init_db()
    logger.info("Database initialization completed.") 