from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.comment import (
    Comment, 
    CommentCreate, 
    CommentUpdate, 
    CommentWithClassification
)
from app.services.auth import get_current_user
from app.services.comments import (
    get_comments, 
    get_comment_by_id, 
    create_comment,
    update_comment,
    delete_comment,
    whitelist_comment,
    classify_comment
)

router = APIRouter()

@router.get("/", response_model=List[CommentWithClassification])
async def list_comments(
    video_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve comments with optional filtering
    """
    comments = get_comments(
        db, 
        user_id=current_user.id,
        video_id=video_id,
        risk_level=risk_level,
        skip=skip, 
        limit=limit
    )
    return comments


@router.get("/{comment_id}", response_model=CommentWithClassification)
async def get_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve a single comment by ID
    """
    comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    return comment


@router.post("/classify", response_model=CommentWithClassification)
async def classify_comment_text(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Classify a comment for spam probability without saving
    """
    classified_comment = classify_comment(comment.content)
    return classified_comment


@router.post("/", response_model=CommentWithClassification)
async def add_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new comment with classification
    """
    return create_comment(db, comment=comment, user_id=current_user.id)


@router.put("/{comment_id}", response_model=CommentWithClassification)
async def edit_comment(
    comment_id: str,
    comment_update: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update a comment by ID
    """
    comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    updated_comment = update_comment(db, comment=comment, comment_update=comment_update)
    return updated_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete a comment by ID
    """
    comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    delete_comment(db, comment=comment)


@router.post("/{comment_id}/whitelist", response_model=CommentWithClassification)
async def add_to_whitelist(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Add a comment to the whitelist
    """
    comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    whitelisted_comment = whitelist_comment(db, comment=comment)
    return whitelisted_comment


@router.post("/batch/delete", status_code=status.HTTP_204_NO_CONTENT)
async def batch_delete_comments(
    comment_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    Delete multiple comments by ID
    """
    for comment_id in comment_ids:
        comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
        if comment:
            delete_comment(db, comment=comment)


@router.post("/batch/whitelist", response_model=List[CommentWithClassification])
async def batch_whitelist_comments(
    comment_ids: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Add multiple comments to the whitelist
    """
    whitelisted_comments = []
    for comment_id in comment_ids:
        comment = get_comment_by_id(db, comment_id=comment_id, user_id=current_user.id)
        if comment:
            whitelisted_comment = whitelist_comment(db, comment=comment)
            whitelisted_comments.append(whitelisted_comment)
    
    return whitelisted_comments 