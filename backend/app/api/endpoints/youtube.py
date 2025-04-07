from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.youtube import (
    Video,
    VideoList,
    Channel,
    ChannelList,
    Comment,
    CommentList,
    CommentAction
)
from app.services.auth import get_current_user
from app.services.youtube import (
    get_channel_info,
    get_user_videos,
    get_video_comments,
    delete_youtube_comment,
    get_video_details
)
from app.services.youtube_api import get_youtube_api

router = APIRouter()

@router.get("/channel", response_model=Channel)
async def get_channel(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get the authenticated user's YouTube channel info
    """
    channel = get_channel_info(youtube_token=current_user.youtube_token)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="YouTube channel not found or not authenticated",
        )
    return channel


@router.get("/videos", response_model=VideoList)
async def list_videos(
    page_token: Optional[str] = None,
    max_results: int = 10,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    List videos from the authenticated user's channel
    """
    videos = get_user_videos(
        youtube_token=current_user.youtube_token,
        page_token=page_token,
        max_results=max_results
    )
    return videos


@router.get("/videos/{video_id}", response_model=Video)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get details for a specific video
    """
    video = get_video_details(
        youtube_token=current_user.youtube_token,
        video_id=video_id
    )
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )
    return video


@router.get("/videos/{video_id}/comments", response_model=CommentList)
async def list_comments(
    video_id: str,
    page_token: Optional[str] = None,
    max_results: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    List comments for a specific video and classify them
    """
    comments = get_video_comments(
        db=db,
        youtube_token=current_user.youtube_token,
        video_id=video_id,
        user_id=current_user.id,
        page_token=page_token,
        max_results=max_results
    )
    return comments


@router.post("/comments/{comment_id}/actions", status_code=status.HTTP_204_NO_CONTENT)
async def perform_comment_action(
    comment_id: str,
    action: CommentAction,
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Perform an action on a comment (delete)
    """
    if action.action_type == "delete":
        success = delete_youtube_comment(
            youtube_token=current_user.youtube_token,
            comment_id=comment_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete comment",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported action: {action.action_type}",
        )


@router.get("/videos/{video_id}/public-comments")
async def get_public_comments(
    video_id: str,
    max_results: int = 100,
) -> Any:
    """
    Get public comments for a YouTube video using API key
    """
    try:
        # Get API key from environment
        from app.core.config import get_settings
        settings = get_settings()
        api_key = settings.YOUTUBE_API_KEY
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="YouTube API key not configured"
            )
            
        # Use YouTube API to fetch comments
        youtube_api = get_youtube_api(api_key)
        comments = youtube_api.get_video_comments(video_id, max_results)
        
        # Return comments
        return {
            "video_id": video_id,
            "comments": comments,
            "count": len(comments)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch YouTube comments: {str(e)}"
        ) 