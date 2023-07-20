from __future__ import annotations

from hertavilla import (
    VillaBot,
    init_backend,
    run as villa_run,
)
from hertavilla.server.fastapi import FastAPIBackend

_bot: VillaBot | None = None


def init_bot(bot_id: str, secret: str, pub_key: str):
    global _bot
    init_backend(FastAPIBackend)
    _bot = VillaBot(bot_id, secret, "/", pub_key)


def get_bot() -> VillaBot:
    if _bot is None:
        raise RuntimeError("Bot is not initialized")
    return _bot


def run(host: str, port: int):
    if _bot is None:
        raise RuntimeError("Bot is not initialized")
    villa_run(_bot, host=host, port=port)
