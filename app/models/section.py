from datetime import datetime, timezone
from typing import Any, Optional
from sqlalchemy import DateTime, Integer, String, Text, JSON, Boolean, Column
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Section(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sort_order = Column(Integer, nullable=False, default=0, index=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[Optional[str]| None] = mapped_column(
        Text,
        nullable=True,
    )
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )

    # Status
    # Example:
    # available
    # sold
    # rented
    status: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    # Flexible features JSON
    # Example:
    # {
    #   "rooms": 3,
    #   "bathrooms": 2,
    #   "surface": "110m²",
    #   "icons": [...]
    # }
    features: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
    )
    images = Column(JSON, nullable=True)   # lista di {"url": "...", "path": "..."}
    meta: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    is_published: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )