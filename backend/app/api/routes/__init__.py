from fastapi import APIRouter
from app.api.routes import spam_detection, users, comments, ml_settings

# Main API router
api_router = APIRouter()

# Include spam detection routes
api_router.include_router(
    spam_detection.router,
    prefix="/spam-detection",
    tags=["spam-detection"]
)

# Include user management routes
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

# Include comments management routes
api_router.include_router(
    comments.router,
    prefix="/comments",
    tags=["comments"]
)

# Include ML settings routes
api_router.include_router(
    ml_settings.router,
    prefix="/ml-settings",
    tags=["ml-settings"]
) 