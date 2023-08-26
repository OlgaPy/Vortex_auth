import logging

import jinja2
from fastapi import FastAPI

from app.core.settings import settings
from app.v1.urls import router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(levelname)s %(asctime)s %(name)s %(message)s",
)

app = FastAPI(title=settings.title, version=settings.version, debug=settings.debug)

app.include_router(router, prefix="/v1")

templates = jinja2.Environment(
    loader=jinja2.PackageLoader("app", "templates"),
    autoescape=jinja2.select_autoescape(["html", "txt"]),
)
