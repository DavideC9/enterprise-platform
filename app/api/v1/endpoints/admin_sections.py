import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.core.media import save_upload_file
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.section import SectionListOut, SectionOut, SectionCreate, SectionUpdate, ReorderRequest
from app.services.section_service import SectionService

router = APIRouter()


def _parse_json_field(value: Optional[str], field_name: str) -> Optional[dict | list]:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be valid JSON",
        )


@router.get("", response_model=SectionListOut, summary="List all sections (admin)")
async def admin_list_sections(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        published_only: bool = Query(False),
        db: AsyncSession = Depends(get_db),
        _admin: AdminUser = Depends(get_current_admin),
):
    total, items = await SectionService.get_all(
        db, published_only=published_only, skip=skip, limit=limit
    )
    return SectionListOut(total=total, items=items)


@router.post("", response_model=SectionOut, status_code=status.HTTP_201_CREATED, summary="Create section")
async def create_section(
        key: str = Form(...),
        slug: str = Form(...),
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        status_value: Optional[str] = Form(None, alias="status"),
        features: Optional[str] = Form(None, description="JSON string"),
        meta: Optional[str] = Form(None, description="JSON string"),
        is_published: bool = Form(True),
        images: Optional[List[UploadFile]] = File(None),
        db: AsyncSession = Depends(get_db),
        _admin: AdminUser = Depends(get_current_admin),
):
    existing = await SectionService.get_by_key(db, key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Section '{key}' already exists. Use PUT to update.",
        )

    saved_images = []
    if images:
        for img in images:
            if img.filename:
                result = await save_upload_file(img, subfolder=f"sections/{key}")
                saved_images.append({
                    "url": result["public_url"],
                    "path": result["relative_path"],
                })

    data = SectionCreate(
        key=key,
        slug=slug,
        title=title,
        description=description,
        address=address,
        status=status_value,
        features=_parse_json_field(features, "features"),
        meta=_parse_json_field(meta, "meta"),
        is_published=is_published,
        images=saved_images or None,
    )
    section = await SectionService.create(db, data)
    await db.commit()
    return section


@router.put("/{key}", response_model=SectionOut, summary="Update section")
async def update_section(
        key: str,
        slug: Optional[str] = Form(None),
        title: Optional[str] = Form(None),
        description: Optional[str] = Form(None),
        address: Optional[str] = Form(None),
        status_value: Optional[str] = Form(None, alias="status"),
        features: Optional[str] = Form(None, description="JSON string"),
        meta: Optional[str] = Form(None, description="JSON string"),
        is_published: Optional[bool] = Form(None),
        images: Optional[List[UploadFile]] = File(None),
        existing_images: Optional[str] = Form(None, description="JSON array delle immagini già salvate da mantenere"),
        db: AsyncSession = Depends(get_db),
        _admin: AdminUser = Depends(get_current_admin),
):
    section = await SectionService.get_by_key(db, key)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section '{key}' not found",
        )

    # existing_images assente → non toccare le immagini (None)
    # existing_images presente (anche []) → sostituisci con kept + new
    final_images: Optional[list] = None

    if existing_images is not None:
        kept: list = _parse_json_field(existing_images, "existing_images") or []

        new_saved = []
        if images:
            for img in images:
                if img.filename:
                    result = await save_upload_file(img, subfolder=f"sections/{key}")
                    new_saved.append({
                        "url": result["public_url"],
                        "path": result["relative_path"],
                    })

        final_images = kept + new_saved
        kept_paths = {img["path"] for img in kept if img.get("path")}
    else:
        # Nessuna gestione immagini in questo aggiornamento
        kept_paths = None

    data = SectionUpdate(
        slug=slug,
        title=title,
        description=description,
        address=address,
        status=status_value,
        features=_parse_json_field(features, "features"),
        meta=_parse_json_field(meta, "meta"),
        is_published=is_published,
        images=final_images,  # None se existing_images non è stato mandato
    )

    section = await SectionService.update(
        db=db,
        section=section,
        data=data,
        kept_image_paths=kept_paths,
    )
    await db.commit()
    return section

@router.patch("/reorder", summary="Reorder sections")
async def reorder_sections(
    body: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    _admin: AdminUser = Depends(get_current_admin),
):
    for item in body.items:
        section = await SectionService.get_by_key(db, item.key)
        if section:
            section.sort_order = item.sort_order
    await db.commit()
    return {"updated": len(body.items)}

@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete section")
async def delete_section(
        key: str,
        db: AsyncSession = Depends(get_db),
        _admin: AdminUser = Depends(get_current_admin),
):
    section = await SectionService.get_by_key(db, key)
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section '{key}' not found",
        )
    await SectionService.delete(db, section)
    await db.commit()