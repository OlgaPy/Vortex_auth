import os

from pydantic import BaseModel
from yaml import safe_load

__all__ = ["config", "Config"]


class Config(BaseModel):
    """Конфиг сервиса."""


_config_path = os.getenv("CONFIG_PATH", "./config.yaml")
with open(_config_path, "r", encoding="utf-8") as stream:
    config = Config.model_validate(safe_load(stream))
