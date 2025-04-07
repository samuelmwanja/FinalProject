from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.metrics import (
    OverallMetrics,
    VideoMetrics,
    TimeSeriesMetrics,
    MostTargetedVideos
)
from app.services.auth import get_current_user
from app.services.metrics import (
    get_overall_metrics,
    get_video_metrics,
    get_time_series_metrics,
    get_most_targeted_videos,
    get_dashboard_metrics
)

router = APIRouter()

@router.get("/dashboard", response_model=Dict[str, Any])
async def get_metrics_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get metrics for dashboard display
    """
    metrics = get_dashboard_metrics(db, user_id=current_user.id)
    return metrics


@router.get("/overall", response_model=OverallMetrics)
async def get_metrics_overall(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get overall metrics for the user
    """
    metrics = get_overall_metrics(db, user_id=current_user.id)
    return metrics


@router.get("/video/{video_id}", response_model=VideoMetrics)
async def get_metrics_for_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get metrics for a specific video
    """
    metrics = get_video_metrics(db, video_id=video_id, user_id=current_user.id)
    return metrics


@router.get("/timeseries", response_model=TimeSeriesMetrics)
async def get_timeseries_metrics(
    period: str = "day",
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get time series metrics (day, week, month)
    """
    metrics = get_time_series_metrics(
        db, 
        user_id=current_user.id,
        period=period,
        limit=limit
    )
    return metrics


@router.get("/most-targeted", response_model=MostTargetedVideos)
async def get_targeted_videos(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get most targeted videos by spam
    """
    videos = get_most_targeted_videos(db, user_id=current_user.id, limit=limit)
    return {"videos": videos} 