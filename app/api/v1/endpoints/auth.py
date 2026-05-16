from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.admin import AdminUser
from app.schemas.auth import AdminOut, LoginRequest, TokenResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Admin login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == payload.email)
    )
    admin: AdminUser | None = result.scalar_one_or_none()

    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled",
        )

    # Update last_login
    admin.last_login = datetime.now(timezone.utc)
    await db.commit()

    token = create_access_token(subject=admin.email)
    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=AdminOut, summary="Current admin info")
async def me(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(__import__("app.api.deps", fromlist=["get_current_admin"]).get_current_admin),
):
    return current_admin