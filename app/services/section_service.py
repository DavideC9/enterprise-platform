from typing import List, Optional, Set
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.section import Section
from app.core.media import delete_media_file
from app.schemas.section import SectionCreate, SectionUpdate


class SectionService:

    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[Section]:
        result = await db.execute(select(Section).where(Section.key == key))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        db: AsyncSession,
        published_only: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[int, List[Section]]:
        query = select(Section).order_by(
            Section.sort_order.asc(),
            Section.created_at.desc()
        )
        count_q = select(func.count()).select_from(Section)
        if published_only:
            query = query.where(Section.is_published == True)
            count_q = count_q.where(Section.is_published == True)
        total = (await db.execute(count_q)).scalar_one()
        items = (await db.execute(query.offset(skip).limit(limit))).scalars().all()
        return total, list(items)

    @staticmethod
    async def create(db: AsyncSession, data: SectionCreate) -> Section:
        section = Section(
            key=data.key,
            slug=data.slug,
            title=data.title,
            description=data.description,
            address=data.address,
            status=data.status,
            features=data.features,
            meta=data.meta,
            is_published=data.is_published,
            images=data.images or None,
        )
        db.add(section)
        await db.flush()
        await db.refresh(section)
        return section

    @staticmethod
    async def update(
        db: AsyncSession,
        section: Section,
        data: SectionUpdate,
        kept_image_paths: Optional[Set[str]] = None,
    ) -> Section:
        if data.slug is not None:
            section.slug = data.slug
        if data.title is not None:
            section.title = data.title
        if data.description is not None:
            section.description = data.description
        if data.address is not None:
            section.address = data.address
        if data.status is not None:
            section.status = data.status
        if data.features is not None:
            section.features = data.features
        if data.meta is not None:
            section.meta = data.meta
        if data.is_published is not None:
            section.is_published = data.is_published

        # images=None → non toccare
        # images=[]   → rimuovi tutte
        # images=[..] → sostituisci
        if data.images is not None:
            for img in (section.images or []):
                path = img.get("path") if isinstance(img, dict) else None
                if path and (kept_image_paths is None or path not in kept_image_paths):
                    delete_media_file(path)
            section.images = data.images if data.images else None

        await db.flush()
        await db.refresh(section)
        return section

    @staticmethod
    async def delete(db: AsyncSession, section: Section) -> None:
        for img in (section.images or []):
            path = img.get("path") if isinstance(img, dict) else None
            if path:
                delete_media_file(path)
        await db.delete(section)
        await db.flush()