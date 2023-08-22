from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_all():
    ...


@router.delete("/all")
def delete_all():
    ...


@router.delete("/{session_id}")
def delete_one(session_id: str):
    ...
