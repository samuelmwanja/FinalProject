from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    content: str
    author_name: Optional[str] = None
    author_channel_id: Optional[str] = None
    youtube_video_id: Optional[str] = None
    youtube_comment_id: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    is_spam: Optional[bool] = None
    spam_probability: Optional[float] = None
    risk_level: Optional[str] = None
    is_whitelisted: Optional[bool] = None


class Comment(CommentBase):
    id: UUID
    user_id: UUID
    youtube_channel_id: str
    published_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True


class CommentWithClassification(Comment):
    spam_probability: float
    risk_level: str = "low"
    is_spam: bool = False
    is_deleted: bool = False
    is_whitelisted: bool = False
    is_auto_moderated: bool = False
    moderation_action: str = "none"
    detection_features: Optional[Dict[str, Any]] = None 