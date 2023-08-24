from pydantic import BaseModel


class HTTPResponse(BaseModel):
    """Basic response schema for HTTPException."""

    detail: str
