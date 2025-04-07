from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Thumbnail(BaseModel):
    url: HttpUrl
    width: int
    height: int


class Video(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    published_at: datetime
    thumbnail_url: Optional[HttpUrl] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    duration: Optional[str] = None
    channel_id: str
    channel_title: str


class VideoList(BaseModel):
    items: List[Video]
    next_page_token: Optional[str] = None
    total_results: int


class Channel(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    published_at: datetime
    thumbnail_url: Optional[HttpUrl] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
    country: Optional[str] = None


class ChannelList(BaseModel):
    items: List[Channel]
    next_page_token: Optional[str] = None
    total_results: int


class Comment(BaseModel):
    id: str
    text: str
    author_display_name: str
    author_profile_image_url: Optional[HttpUrl] = None
    author_channel_id: str
    video_id: str
    parent_id: Optional[str] = None
    published_at: datetime
    updated_at: Optional[datetime] = None
    like_count: Optional[int] = None
    spam_probability: Optional[float] = None
    risk_level: Optional[str] = None


class CommentList(BaseModel):
    items: List[Comment]
    next_page_token: Optional[str] = None
    total_results: int


class CommentAction(BaseModel):
    action_type: str = Field(..., description="Action to perform on comment (delete)")
    metadata: Optional[Dict[str, Any]] = None 