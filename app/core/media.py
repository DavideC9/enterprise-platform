from app.core import log_config
import mimetypes
import re
import uuid
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

import logging as _logging
logger = _logging.getLogger(__name__)

# Subdirectories created automatically under MEDIA_ROOT
MEDIA_SUBDIRS = ["sections", "uploads", "tmp"]


def ensure_media_dirs() -> None:
    """Create media root and all subdirectories on startup."""
    settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    for sub in MEDIA_SUBDIRS:
        (settings.MEDIA_ROOT / sub).mkdir(parents=True, exist_ok=True)
    logger.info(f"Media directories ready at {settings.MEDIA_ROOT}")


def sanitize_filename(filename: str) -> str:
    """Return a safe, lowercase filename without path traversal."""
    filename = Path(filename).name
    filename = re.sub(r"[^\w.\-]", "_", filename).lower()
    return filename


def build_unique_filename(original: str) -> str:
    """
    Keep original filename and append a short unique id.

    Example:
    cucina-moderna_a8f42c.jpg
    """

    original = sanitize_filename(original)

    path = Path(original)

    stem = path.stem
    suffix = path.suffix.lower() or ".bin"

    # ID corto
    short_id = uuid.uuid4().hex[:6]

    return f"{stem}_{short_id}{suffix}"


def get_media_path(subfolder: str, filename: str) -> Path:
    folder = settings.MEDIA_ROOT / subfolder
    folder.mkdir(parents=True, exist_ok=True)
    return folder / filename


def build_public_url(relative_path: str) -> str:
    """Build the full public URL for a stored media file."""
    return f"{settings.PUBLIC_BASE_URL}{settings.MEDIA_URL}/{relative_path}"


async def save_upload_file(
    file: UploadFile,
    subfolder: str = "uploads",
    custom_name: Optional[str] = None,
) -> dict:
    """
    Validate and persist an uploaded image to disk.
    Returns a dict with relative_path and public_url.
    """
    # ── Validate content type ────────────────────────────────────────────
    content_type = file.content_type or ""
    if content_type not in settings.ALLOWED_IMAGE_TYPES:
        # Try to detect from extension as fallback
        guessed, _ = mimetypes.guess_type(file.filename or "")
        if guessed not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{content_type}' not allowed. Allowed: {settings.ALLOWED_IMAGE_TYPES}",
            )

    # ── Read & validate size ─────────────────────────────────────────────
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    # ── Persist ──────────────────────────────────────────────────────────
    safe_name = custom_name or build_unique_filename(file.filename or "image")
    dest = get_media_path(subfolder, safe_name)
    dest.write_bytes(data)

    relative_path = f"{subfolder}/{safe_name}"
    logger.info(f"Saved upload: {dest}")

    return {
        "filename": safe_name,
        "relative_path": relative_path,
        "public_url": build_public_url(relative_path),
        "size_bytes": len(data),
        "content_type": content_type,
    }


def delete_media_file(relative_path: str) -> bool:
    """Delete a media file by its relative path. Returns True if deleted."""
    full = settings.MEDIA_ROOT / relative_path
    if full.exists() and full.is_file():
        full.unlink()
        logger.info(f"Deleted media file: {full}")
        return True
    return False