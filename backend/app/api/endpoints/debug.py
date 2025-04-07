from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.scripts.add_test_data import add_test_data

router = APIRouter()

@router.post("/add-test-data", status_code=status.HTTP_201_CREATED)
def add_test_data_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add test data to the database.
    This endpoint is for development and testing purposes only.
    """
    # Only allow this in development
    import os
    if os.getenv("ENV", "development") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is not available in production"
        )
    
    try:
        add_test_data()
        return {"status": "success", "message": "Test data added successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add test data: {str(e)}"
        ) 