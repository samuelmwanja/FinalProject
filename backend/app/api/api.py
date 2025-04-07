from fastapi import APIRouter

from app.api.endpoints import auth, comments, metrics, ml_settings, users, debug

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(ml_settings.router, prefix="/ml-settings", tags=["ml-settings"])
api_router.include_router(debug.router, prefix="/debug", tags=["debug"]) 