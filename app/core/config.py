from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "CMS Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    ALGORITHM: str = "HS256"

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    # CORS
    # Tipo str per evitare che pydantic-settings tenti json.loads automatico.
    # Il validator sotto converte tutto in List[str].
    BACKEND_CORS_ORIGINS_RAW: str = "*"

    @property
    def BACKEND_CORS_ORIGINS(self) -> List[str]:
        v = self.BACKEND_CORS_ORIGINS_RAW.strip()
        if v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                pass
        return [i.strip() for i in v.split(",") if i.strip()]

    # Upload
    MEDIA_ROOT: Path = Path("/media")
    MEDIA_URL: str = "/media"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp", "image/gif"]

    @property
    def MAX_UPLOAD_SIZE_BYTES(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    PUBLIC_BASE_URL: str = "http://localhost:8000"


settings = Settings()