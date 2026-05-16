from fastapi import APIRouter

from app.api.v1.endpoints import auth, content, admin_sections, media

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Public content routes
api_router.include_router(content.router, prefix="/content", tags=["content"])

# Admin routes (all protected)
api_router.include_router(admin_sections.router, prefix="/admin/sections", tags=["admin"])
api_router.include_router(media.router, prefix="/admin/media", tags=["admin"])