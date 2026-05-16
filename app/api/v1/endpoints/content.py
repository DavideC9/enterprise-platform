from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.section import SectionListOut, SectionOut
from app.services.section_service import SectionService

router = APIRouter()


@router.get("", response_model=SectionListOut, summary="List all published sections")
async def list_sections(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    total, items = await SectionService.get_all(db, published_only=True, skip=skip, limit=limit)
    return SectionListOut(total=total, items=items)


@router.get("/{key}", response_model=SectionOut, summary="Get section by key")
async def get_section(key: str, db: AsyncSession = Depends(get_db)):
    section = await SectionService.get_by_key(db, key)
    if not section or not section.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Section '{key}' not found",
        )
    return section