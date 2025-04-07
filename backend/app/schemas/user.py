from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    youtube_channel_id: Optional[str] = None
    youtube_channel_name: Optional[str] = None
    
    class Config:
        orm_mode = True
        from_attributes = True


class UserResponse(UserInDBBase):
    pass


class UserInDB(UserInDBBase):
    hashed_password: str 