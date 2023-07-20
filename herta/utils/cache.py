from __future__ import annotations

import json
from typing import Any

from herta.utils.const import ENCODING
from herta.utils.resource import resource

from hertavilla import get_backend

backend = get_backend()


class Cache:
    def __init__(self, name: str) -> None:
        self.path = resource("cache") / f"{name}.json"
        if not self.path.exists():
            self.path.write_text("{}")
        self.data = json.loads(self.path.read_text(encoding=ENCODING))
        backend.on_shutdown(self.save_data)

    def __getitem__(self, key: str) -> Any:
        return self.data.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.data[key] = value

    async def save_data(self) -> None:
        self.path.write_text(json.dumps(self.data), encoding=ENCODING)
