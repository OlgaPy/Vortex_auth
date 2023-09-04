from fastapi import APIRouter, Body, Depends, Request
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app import deps
from app.core.settings import settings

router = APIRouter()


@router.post("/confirm")
def confirm_code(
    request: Request,
    code: str = Body(
        embed=True,
        max_length=settings.confirmation_code_length,
        min_length=settings.confirmation_code_length,
        pattern="^[a-f0-9]+$",
    ),
    db: Session = Depends(deps.get_db),
    redis: Redis = Depends(deps.get_redis),
):
    ...
    # По коду получить из redis user uuid и тип активации
    # Активировать юзера, заполнив <code_type>_activated_at
    # Если все активации пройдены - поставить флаг is_active=True и обновить на монолите
    # Сгенерировать / обновить JWT token и отправить клиенту


@router.post("/")
def request_code():
    ...
