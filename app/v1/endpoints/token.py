from fastapi import APIRouter

router = APIRouter()


@router.post("/refresh")
def refresh():
    ...
