from fastapi import APIRouter

router = APIRouter()


@router.post("/reset")
def reset():
    ...


@router.post("/confirm")
def confirm():
    ...
