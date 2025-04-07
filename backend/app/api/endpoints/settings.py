from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.settings import MLSettings, MLSettingsUpdate
from app.services.auth import get_current_user
from app.services.settings import get_ml_settings, update_ml_settings

router = APIRouter()

@router.get("/ml", response_model=MLSettings)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the current ML settings for the user
    """
    settings = get_ml_settings(db, user_id=current_user.id)
    if not settings:
        # Create default settings if none exist
        settings = update_ml_settings(
            db,
            user_id=current_user.id,
            settings=MLSettingsUpdate(
                sensitivity=75,
                keywords=["sub4sub", "check my channel", "free gift", "click my profile"],
                bot_patterns=["^[A-Za-z0-9]+bot$", ".*\\d{3}$"],
                auto_delete=False
            )
        )
    return settings


@router.put("/ml", response_model=MLSettings)
async def update_settings(
    settings_update: MLSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update the ML settings for the user
    """
    settings = update_ml_settings(
        db,
        user_id=current_user.id,
        settings=settings_update
    )
    return settings 