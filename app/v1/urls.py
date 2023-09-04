from fastapi import APIRouter

from app.v1.endpoints import code, password, session, token, user

router = APIRouter()

router.include_router(code.router, prefix="/code", tags=["code"])
router.include_router(password.router, prefix="/password", tags=["password"])
router.include_router(session.router, prefix="/session", tags=["session"])
router.include_router(token.router, prefix="/token", tags=["token"])
router.include_router(user.router, prefix="/user", tags=["user"])
