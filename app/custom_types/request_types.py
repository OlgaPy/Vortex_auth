from typing import Annotated

from fastapi import Body, Header

UserAgent = Annotated[str | None, Header()]

RefreshToken = Annotated[str, Body(embed=True)]
