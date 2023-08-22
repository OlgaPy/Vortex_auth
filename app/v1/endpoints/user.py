from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
def register():
    ...


@router.post("/login")
def login():
    ...
