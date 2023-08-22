from fastapi import APIRouter

router = APIRouter()


@router.post("/confirm")
def confirm_code():
    ...


@router.post("/")
def request_code():
    ...
