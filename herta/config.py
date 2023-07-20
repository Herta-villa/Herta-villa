from __future__ import annotations

from pydantic import BaseSettings, Extra
from pydantic.env_settings import (
    DotenvType,
)


class Setting(BaseSettings):
    _env_file: DotenvType = ".env", ".env.prod", ".env.dev"

    host: str = "0.0.0.0"
    port: int = 8080

    bot_id: str = ""
    bot_secret: str = ""
    bot_pub_key: str = ""

    class Config:
        extra = Extra.allow
