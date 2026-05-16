from fastapi import APIRouter, Depends, File, Form, UploadFile
from typing import Optional

from app.api.deps import get_current_admin
from app.core.media import save_upload_file
from app.models.admin import AdminUser
from app.schemas.media import UploadOut

router = APIRouter()


@router.post("", response_model=UploadOut, summary="Upload image to media folder")
async def upload_image(
    file: UploadFile = File(...),
    folder: Optional[str] = Form("uploads", description="Subfolder inside /media"),
    _admin: AdminUser = Depends(get_current_admin),
):
    """
    Upload any image to the server.
    Returns the public URL that can then be stored in a section's `image_url`.
    """
    result = await save_upload_file(file, subfolder=folder)
    return UploadOut(**result)