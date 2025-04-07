import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, Boolean, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # YouTube specific
    youtube_comment_id = Column(String, unique=True, index=True, nullable=False)
    youtube_video_id = Column(String, nullable=False, index=True)
    youtube_channel_id = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    author_name = Column(String, nullable=False)
    author_channel_id = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    
    # Spam classification
    spam_probability = Column(Float, nullable=False, default=0.0)
    risk_level = Column(Enum("low", "medium", "high", name="risk_level_enum"), nullable=False, default="low")
    is_spam = Column(Boolean, default=False)
    detection_features = Column(JSON, nullable=True)  # Store features used in detection
    
    # Actions
    is_deleted = Column(Boolean, default=False)
    is_whitelisted = Column(Boolean, default=False)
    is_auto_moderated = Column(Boolean, default=False)
    moderation_action = Column(Enum("none", "deleted", "reported", "whitelisted", name="moderation_action_enum"), default="none")
    moderated_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="comments")
    
    def __repr__(self):
        return f"<Comment {self.youtube_comment_id[:8]}... by {self.author_name}>" 