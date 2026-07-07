from fastapi import APIRouter

from app.config import settings
from app.database import get_public_database_status

router = APIRouter(prefix="/api", tags=["System"])


@router.get("/status")
async def status():
    return {
        "app": settings.app_name,
        "status": "Online",
        "workflow": "document_upload_binary_gridfs_matching",
    }


@router.get("/health")
async def health():
    return {"api": "Online", "database": get_public_database_status()}
