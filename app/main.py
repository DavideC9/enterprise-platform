import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.log_config import setup_logging
from app.db.init_db import init_db, seed_admin
from app.db.session import engine
from app.core.media import ensure_media_dirs

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CMS Backend...")
    ensure_media_dirs()

    async with engine.begin() as conn:
        await init_db(conn)

    await seed_admin()

    logger.info("CMS Backend ready.")
    yield
    logger.info("Shutting down CMS Backend.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-ready CMS Backend API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # List[str]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media", StaticFiles(directory=str(settings.MEDIA_ROOT)), name="media")
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": settings.VERSION}