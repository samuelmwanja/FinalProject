from fastapi import APIRouter

from app.api.endpoints import auth, comments, metrics, settings, youtube

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(comments.router, prefix="/comments", tags=["Comments"])
router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
router.include_router(settings.router, prefix="/settings", tags=["Settings"])
router.include_router(youtube.router, prefix="/youtube", tags=["YouTube"]) 