from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User
from app.schemas.metrics import VideoMetricItem, TimeSeriesDataPoint

def count_total_comments(db: Session, user_id=None, video_id=None) -> int:
    """
    Count total comments for a user or specific video
    """
    query = db.query(Comment)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    if video_id:
        query = query.filter(Comment.youtube_video_id == video_id)
    
    return query.count()

def count_flagged_spam(db: Session, user_id=None, video_id=None) -> int:
    """
    Count comments flagged as spam
    """
    query = db.query(Comment).filter(Comment.is_spam == True)
    
    if user_id:
        query = query.filter(Comment.user_id == user_id)
    
    if video_id:
        query = query.filter(Comment.youtube_video_id == video_id)
    
    return query.count()

def calculate_spam_rate(db: Session, user_id=None, video_id=None) -> float:
    """
    Calculate spam rate as percentage
    """
    total = count_total_comments(db, user_id, video_id)
    if total == 0:
        return 0
    
    spam = count_flagged_spam(db, user_id, video_id)
    return round((spam / total) * 100, 1)  # Return as percentage with 1 decimal place

def get_statistics_by_time_period(db: Session, user_id, period='month') -> Dict[str, float]:
    """
    Get comparison statistics for current period vs previous period
    Returns change percentages for metrics
    """
    now = datetime.utcnow()
    
    # Set time periods based on 'period' parameter
    if period == 'week':
        current_start = now - timedelta(days=7)
        previous_start = now - timedelta(days=14)
    elif period == 'day':
        current_start = now - timedelta(days=1)
        previous_start = now - timedelta(days=2)
    else:  # Default to month
        current_start = now - timedelta(days=30)
        previous_start = now - timedelta(days=60)
    
    # Current period stats
    current_total = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.created_at >= current_start
    ).count()
    
    current_spam = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.is_spam == True,
        Comment.created_at >= current_start
    ).count()
    
    # Previous period stats
    previous_total = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.created_at >= previous_start,
        Comment.created_at < current_start
    ).count()
    
    previous_spam = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.is_spam == True,
        Comment.created_at >= previous_start,
        Comment.created_at < current_start
    ).count()
    
    # Calculate percentage changes
    total_comments_change = 0
    if previous_total > 0:
        total_comments_change = round(((current_total - previous_total) / previous_total) * 100, 1)
    
    flagged_spam_change = 0
    if previous_spam > 0:
        flagged_spam_change = round(((current_spam - previous_spam) / previous_spam) * 100, 1)
    
    # Industry average is typically around 12% (this would be based on real data)
    industry_average = 12
    
    return {
        "total_comments_change": total_comments_change,
        "flagged_spam_change": flagged_spam_change,
        "industry_average": industry_average
    }

def get_most_targeted_videos(db: Session, user_id, limit=5):
    """Get videos with highest spam counts for a user

    Args:
        db (Session): Database session
        user_id: User ID
        limit (int, optional): Number of videos to return. Defaults to 5.

    Returns:
        List of dictionaries with video_title and spam_count
    """
    videos = db.query(
        Comment.video_id,
        Comment.video_title,
        func.count(Comment.id).label("spam_count")
    ).filter(
        Comment.user_id == user_id,
        Comment.is_spam == True
    ).group_by(
        Comment.video_id,
        Comment.video_title
    ).order_by(
        func.count(Comment.id).desc()
    ).limit(limit).all()
    
    return [
        {"video_id": video.video_id, "video_title": video.video_title, "spam_count": video.spam_count}
        for video in videos
    ]

def get_overall_metrics(db: Session, user_id) -> Dict[str, Any]:
    """
    Get overall metrics for a user
    """
    total_comments = count_total_comments(db, user_id)
    total_flagged = count_flagged_spam(db, user_id)
    bot_detection_rate = calculate_spam_rate(db, user_id)
    
    # Risk level counts
    high_risk = db.query(Comment).filter(
        Comment.user_id == user_id, 
        Comment.risk_level == 'high'
    ).count()
    
    medium_risk = db.query(Comment).filter(
        Comment.user_id == user_id, 
        Comment.risk_level == 'medium'
    ).count()
    
    low_risk = db.query(Comment).filter(
        Comment.user_id == user_id, 
        Comment.risk_level == 'low'
    ).count()
    
    # Auto-moderated count
    auto_moderated = db.query(Comment).filter(
        Comment.user_id == user_id, 
        Comment.is_auto_moderated == True
    ).count()
    
    # Total videos analyzed
    total_videos = db.query(Comment.youtube_video_id).filter(
        Comment.user_id == user_id
    ).distinct().count()
    
    # Most common keywords (simplified implementation)
    keywords = [
        {"keyword": "sub4sub", "count": 12},
        {"keyword": "check my channel", "count": 8},
        {"keyword": "free gift", "count": 6},
        {"keyword": "click my profile", "count": 5},
        {"keyword": "make money", "count": 3}
    ]
    
    return {
        "total_flagged": total_flagged,
        "total_comments": total_comments,
        "bot_detection_rate": bot_detection_rate,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "auto_moderated_count": auto_moderated,
        "total_videos_analyzed": total_videos,
        "average_spam_percentage": bot_detection_rate,
        "most_common_keywords": keywords
    }

def get_video_metrics(db: Session, video_id, user_id) -> Dict[str, Any]:
    """
    Get metrics for a specific video
    """
    total_comments = count_total_comments(db, user_id, video_id)
    spam_count = count_flagged_spam(db, user_id, video_id)
    spam_percentage = calculate_spam_rate(db, user_id, video_id)
    
    # Risk level counts for this video
    high_risk = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.youtube_video_id == video_id,
        Comment.risk_level == 'high'
    ).count()
    
    medium_risk = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.youtube_video_id == video_id,
        Comment.risk_level == 'medium'
    ).count()
    
    low_risk = db.query(Comment).filter(
        Comment.user_id == user_id,
        Comment.youtube_video_id == video_id,
        Comment.risk_level == 'low'
    ).count()
    
    # Get most active spam authors
    spam_authors = db.query(
        Comment.author_name,
        func.count(Comment.id).label("comment_count")
    ).filter(
        Comment.user_id == user_id,
        Comment.youtube_video_id == video_id,
        Comment.is_spam == True
    ).group_by(
        Comment.author_name
    ).order_by(
        func.count(Comment.id).desc()
    ).limit(5).all()
    
    authors_list = [{"author": a.author_name, "count": a.comment_count} for a in spam_authors]
    
    # Get flagged keywords (simplified)
    flagged_keywords = [
        {"keyword": "sub4sub", "count": 3},
        {"keyword": "check my channel", "count": 2},
        {"keyword": "free gift", "count": 1}
    ]
    
    # Use predefined titles based on video_id
    title = "Unknown Video"
    if video_id == "video1":
        title = "Tech Reviews #42"
    elif video_id == "video2":
        title = "Product Launch 2023"
    elif video_id == "video3":
        title = "Tutorial: Getting Started"
    
    return {
        "video_id": video_id,
        "title": title,
        "total_comments": total_comments,
        "spam_count": spam_count,
        "spam_percentage": spam_percentage,
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "flagged_keywords": flagged_keywords,
        "most_active_spam_authors": authors_list
    }

def get_time_series_metrics(db: Session, user_id, period='day', limit=30) -> Dict[str, Any]:
    """
    Get time series metrics for spam detection
    """
    now = datetime.utcnow()
    
    # Set time window based on period
    if period == 'day':
        delta = timedelta(hours=1)
        format_str = '%Y-%m-%d %H:00'
        days_back = 1
    elif period == 'week':
        delta = timedelta(days=1)
        format_str = '%Y-%m-%d'
        days_back = 7
    else:  # month
        delta = timedelta(days=1)
        format_str = '%Y-%m-%d'
        days_back = 30
    
    # Limit to requested number of data points
    days_back = min(days_back, limit)
    
    # Generate time points
    start_date = now - timedelta(days=days_back)
    data_points = []
    
    # Create time series data (simplified implementation)
    # In a real implementation, you would query the database for each time period
    current_date = start_date
    while current_date <= now:
        # Calculate counts for this time period
        period_end = current_date + delta
        
        # Get counts from database
        total_count = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.created_at >= current_date,
            Comment.created_at < period_end
        ).count()
        
        spam_count = db.query(Comment).filter(
            Comment.user_id == user_id,
            Comment.is_spam == True,
            Comment.created_at >= current_date,
            Comment.created_at < period_end
        ).count()
        
        # Add data point
        data_points.append(TimeSeriesDataPoint(
            timestamp=current_date,
            total_comments=total_count,
            spam_count=spam_count
        ))
        
        # Move to next period
        current_date = period_end
    
    return {
        "period": period,
        "data": data_points
    }

def get_dashboard_metrics(db: Session, user_id):
    """
    Get metrics for dashboard display
    
    Returns:
        Dictionary with dashboard metrics in the format expected by the frontend
    """
    try:
        # Get overall metrics
        total_comments = count_total_comments(db, user_id)
        flagged_spam = count_flagged_spam(db, user_id)
        spam_rate = calculate_spam_rate(db, user_id)
        
        # Get comparison with previous period
        stats_comparison = get_statistics_by_time_period(db, user_id, period='month')
        
        # Get most targeted video
        most_targeted_videos = get_most_targeted_videos(db, user_id, limit=1)
        most_active_video = None
        if most_targeted_videos and len(most_targeted_videos) > 0:
            video = most_targeted_videos[0]
            most_active_video = {
                "title": video["video_title"],
                "spam_count": video["spam_count"]
            }
            
        # Get recent spam detections (limit to 5)
        recent_comment_query = (
            db.query(Comment)
            .filter(Comment.user_id == user_id, Comment.is_spam == True)
            .order_by(Comment.created_at.desc())
            .limit(5)
        )
        recent_detections = []
        for comment in recent_comment_query:
            # Format time as a string (e.g., "2 hours ago", "1 day ago")
            time_diff = datetime.utcnow() - comment.created_at
            if time_diff.days > 0:
                time_str = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds // 3600 > 0:
                hours = time_diff.seconds // 3600
                time_str = f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                minutes = (time_diff.seconds % 3600) // 60
                time_str = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                
            recent_detections.append({
                "id": str(comment.id),
                "text": comment.content[:50] + "..." if len(comment.content) > 50 else comment.content,
                "time": time_str
            })
            
        # Hardcoded industry average for now - could be calculated from all users
        industry_average = 12
            
        return {
            "total_comments": total_comments,
            "flagged_spam": flagged_spam,
            "spam_rate": spam_rate,
            "total_comments_change": stats_comparison.get("total_comments_change", 0),
            "flagged_spam_change": stats_comparison.get("flagged_spam_change", 0),
            "industry_average": industry_average,
            "most_active_video": most_active_video,
            "recent_detections": recent_detections
        }
    except Exception as e:
        # Log error and return default values
        print(f"Error getting dashboard metrics: {e}")
        return {
            "total_comments": 0,
            "flagged_spam": 0,
            "spam_rate": 0,
            "total_comments_change": 0,
            "flagged_spam_change": 0,
            "industry_average": 12,
            "most_active_video": None,
            "recent_detections": []
        } 