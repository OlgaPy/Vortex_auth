from fastapi import FastAPI

from app.core.settings import settings
from app.v1.urls import router

app = FastAPI(
    title=settings.postgres_server, version=settings.version, debug=settings.debug
)

app.include_router(router, prefix="/v1")
