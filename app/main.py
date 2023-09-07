import logging

from fastapi import FastAPI, Request
from sentry_sdk.integrations.redis import RedisIntegration
from starlette.responses import JSONResponse

from app.core.exceptions import TokenException
from app.core.settings import settings
from app.v1.urls import router

if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        send_default_pii=True,
        environment=settings.environment,
        integrations=[
            RedisIntegration(),
        ],
    )

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(levelname)s %(asctime)s %(name)s %(message)s",
)

app = FastAPI(title=settings.title, version=settings.version, debug=settings.debug)

app.include_router(router, prefix="/v1")


@app.exception_handler(TokenException)
async def token_exception_handler(request: Request, exc: TokenException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": [{"type": exc.error_type, "msg": exc.message}]},
    )
