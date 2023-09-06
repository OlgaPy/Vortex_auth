from typing import Annotated

from fastapi import Header

UserAgent = Annotated[str | None, Header()]
