from __future__ import annotations

import json
from typing import Any

from utils.const import ENCODING
from utils.resource import resource


class Index:
    def __init__(self, category: str, lang: str = "cn") -> None:
        self.lang = lang

        r = resource("index") / category
        self.name_to_id_file = r / f"name_to_id_{self.lang}.json"
        self.content = r / "main.json"

        self._content: Any | None = None
        self._global_id: str | None = None

    @property
    def global_id(self) -> str | None:
        return self._global_id

    @global_id.setter
    def global_id(self, value: str) -> None:
        self._global_id = value

    def get_id_by_name(self, name: str) -> str:
        names = json.loads(self.name_to_id_file.read_text(encoding=ENCODING))
        if id_ := names.get(name):
            return id_
        raise ValueError("ID not found")

    def set_id_by_name(self, name: str) -> None:
        self.global_id = self.get_id_by_name(name)

    def build_name_to_id_index(self, data: dict[str, str]) -> None:
        self.name_to_id_file.write_text(json.dumps(data), encoding=ENCODING)

    def build_content(self, data: dict[str, str]) -> None:
        self.content.write_text(json.dumps(data), encoding=ENCODING)

    def __getitem__(self, key: str, id_: str | None = None) -> Any:
        if self._content is None:
            self._content = json.loads(
                self.content.read_text(encoding=ENCODING),
            )
        id_ = id_ or self._global_id
        if id_ is None:
            raise ValueError("ID is not set")
        return self._content[id_][key]
