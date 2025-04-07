from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MLSettingsBase(BaseModel):
    sensitivity: int = Field(75, ge=0, le=100)
    keywords: List[str] = []
    bot_patterns: List[str] = []
    auto_delete: bool = False
    high_risk_threshold: float = Field(0.8, ge=0.0, le=1.0)
    medium_risk_threshold: float = Field(0.4, ge=0.0, le=1.0)
    
    @validator('keywords', 'bot_patterns')
    def ensure_unique(cls, v):
        return list(set(v))
    
    @validator('medium_risk_threshold')
    def validate_thresholds(cls, v, values):
        if 'high_risk_threshold' in values and v >= values['high_risk_threshold']:
            raise ValueError('medium_risk_threshold must be less than high_risk_threshold')
        return v


class MLSettingsCreate(MLSettingsBase):
    user_id: UUID


class MLSettingsUpdate(MLSettingsBase):
    sensitivity: Optional[int] = Field(None, ge=0, le=100)
    keywords: Optional[List[str]] = None
    bot_patterns: Optional[List[str]] = None
    auto_delete: Optional[bool] = None
    high_risk_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    medium_risk_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)


class MLSettingsResponse(MLSettingsBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True
        
    @classmethod
    def from_db(cls, db_obj: Dict[str, Any]) -> 'MLSettingsResponse':
        """
        Convert a database object dictionary to this schema
        """
        return cls(**db_obj) 