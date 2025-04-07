import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # YouTube integration
    youtube_token = Column(Text, nullable=True)
    youtube_refresh_token = Column(Text, nullable=True)
    youtube_token_expires = Column(DateTime, nullable=True)
    youtube_channel_id = Column(String, nullable=True)
    youtube_channel_name = Column(String, nullable=True)
    
    # User preferences
    preferences = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>" 