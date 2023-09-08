import logging

from fastapi import FastAPI, Request
from sentry_sdk.integrations.redis import RedisIntegration
from starlette.responses import JSONResponse

from app.core.exceptions import KapibaraException
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

app = FastAPI(
    title=settings.title,
    version=settings.version,
    license_info={
        "name": "Apache 2.0",
        "identifier": "Apache-2.0",
    },
    openapi_tags=[
        {"name": "user", "description": "Регистрация и авторизация пользователей"},
        {"name": "token", "description": "Работа с токенами"},
        {
            "name": "code",
            "description": "Запрос кодов подтверждения для активации аккаунтов",
        },
        {"name": "password", "description": "Сброс и смена паролей"},
        {"name": "session", "description": "Управлениями сессиями пользователей"},
    ],
    debug=settings.debug,
)

app.include_router(router, prefix="/v1")


@app.exception_handler(KapibaraException)
async def base_exception_handler(request: Request, exc: KapibaraException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": [{"type": exc.error_type, "msg": exc.message}]},
    )
