from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel


class VideoMetricItem(BaseModel):
    title: str
    video_id: str
    spam_count: int
    total_comments: int
    spam_percentage: float


class MostTargetedVideos(BaseModel):
    videos: List[VideoMetricItem]


class OverallMetrics(BaseModel):
    total_flagged: int
    total_comments: int
    bot_detection_rate: float  # percentage
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    auto_moderated_count: int
    total_videos_analyzed: int
    average_spam_percentage: float
    most_common_keywords: List[Dict[str, int]]  # e.g. [{"keyword": "sub4sub", "count": 57}]


class VideoMetrics(BaseModel):
    video_id: str
    title: str
    total_comments: int
    spam_count: int
    spam_percentage: float
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    flagged_keywords: List[Dict[str, int]]
    most_active_spam_authors: List[Dict[str, int]]


class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime
    spam_count: int
    total_comments: int


class TimeSeriesMetrics(BaseModel):
    period: str  # "day", "week", "month"
    data: List[TimeSeriesDataPoint] 


def count_total_comments(db, user_id=None, video_id=None):
    """
    Count total comments for a user or specific video
    """
    query = db.query(Comment)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    if video_id:
        query = query.filter(Comment.youtube_video_id == video_id)
    
    return query.count()


def count_flagged_spam(db, user_id=None, video_id=None):
    """
    Count comments flagged as spam
    """
    query = db.query(Comment).filter(Comment.is_spam == True)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    if video_id:
        query = query.filter(Comment.youtube_video_id == video_id)
    
    return query.count()


def calculate_spam_rate(db, user_id=None, video_id=None):
    """
    Calculate spam rate as percentage
    """
    total = count_total_comments(db, user_id, video_id)
    if total == 0:
        return 0
    
    spam = count_flagged_spam(db, user_id, video_id)
    return round((spam / total) * 100, 1)  # Return as percentage with 1 decimal place


def get_statistics_by_time_period(db, user_id, period='month'):
    """
    Get comparison statistics for current period vs previous period
    Returns change percentages for metrics
    """
    # Implementation depends on your reporting needs but would include:
    # - Calculating current period counts
    # - Calculating previous period counts
    # - Computing percentage changes
    
    # For demonstration, return sample data
    return {
        "total_comments_change": 24,  # 24% increase
        "flagged_spam_change": -12,   # 12% decrease
        "industry_average": 12        # 12% industry average 
    } 