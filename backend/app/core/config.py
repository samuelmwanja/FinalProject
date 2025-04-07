import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Build paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "ml", "models")

class Settings(BaseSettings):
    PROJECT_NAME: str = "SpamShield"
    API_V1_STR: str = "/api/v1"
    YOUTUBE_API_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    ML_MODEL_PATH: str = os.path.join(MODELS_DIR, "spam_classifier_model.pkl")
    VECTORIZER_PATH: str = os.path.join(MODELS_DIR, "count_vectorizer.pkl")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

@lru_cache()
def get_settings():
    return Settings() 