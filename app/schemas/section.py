from datetime import datetime
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, field_validator, ConfigDict
import re

class ReorderItem(BaseModel):
    key: str
    sort_order: int

class ReorderRequest(BaseModel):
    items: List[ReorderItem]

class SectionImage(BaseModel):
    url: str
    path: Optional[str] = None

class SectionCreate(BaseModel):
    key: str
    slug: str
    sort_order: Optional[int] = 0
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    is_published: bool = True
    images: Optional[List[Dict[str, Any]]] = None

    @field_validator("key")
    @classmethod
    def key_lowercase_slug(cls, v: str) -> str:
        v = v.strip().lower()
        v = re.sub(r"[^a-z0-9_\-]", "_", v)
        if not v:
            raise ValueError("key must not be empty")
        return v


class SectionUpdate(BaseModel):
    slug: Optional[str] = None
    sort_order: Optional[int] = 0
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    is_published: Optional[bool] = None
    images: Optional[List[Dict[str, Any]]] = None  # None = non toccare, [] = rimuovi tutte


class SectionOut(BaseModel):
    id: int
    key: str
    sort_order: int = 0
    slug: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    status: Optional[str] = None
    features: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    images: Optional[List[SectionImage]] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SectionListOut(BaseModel):
    total: int
    items: List[SectionOut]