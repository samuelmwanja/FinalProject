import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class MLSettings(Base):
    __tablename__ = "ml_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Spam detection settings
    sensitivity = Column(Integer, default=75)  # 0-100 scale
    keywords = Column(JSON, default=list)  # List of spam keywords
    bot_patterns = Column(JSON, default=list)  # List of regex patterns for bot detection
    auto_delete = Column(Boolean, default=False)  # Auto-delete high confidence spam
    
    # Additional settings
    high_risk_threshold = Column(Float, default=0.8)  # Probability threshold for high risk
    medium_risk_threshold = Column(Float, default=0.4)  # Probability threshold for medium risk
    
    # Metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="ml_settings")
    
    def __repr__(self):
        return f"<MLSettings for user {self.user_id}>" 