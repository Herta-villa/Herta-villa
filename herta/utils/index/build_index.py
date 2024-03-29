from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any

from herta.log import logger
from herta.utils.const import LANG
from herta.utils.index.index import Index
from herta.utils.resource import resource, sr_res

from aiohttp import ClientSession

r = resource("index")


class Builder:
    def __init__(self, category: str, lang: str = "cn") -> None:
        self.category = category
        self._raw: Any | None = None
        self._raw_: Any | None = None
        self.lang = lang
        self.index = Index(category, lang)

    @property
    def raw(self) -> Any:
        if self._raw is None:
            raise ValueError("Raw index is not initialized")
        return self._raw

    async def init_raw(self) -> None:
        logger.info(
            "从 Mar-7th/StarRailRes 拉取 index: "
            f"{self.category}.json (语言: {self.lang})",
        )
        url = sr_res(f"/index_new/{self.lang}/{self.category}.json")
        async with ClientSession() as client:
            async with client.get(
                url,
            ) as resp:
                logger.debug(f"URL: {url}")
                self._raw_ = await resp.read()
                logger.trace(f"Fetched: {self._raw_}")
                self._raw = json.loads(self._raw_)

    def build_name_to_id_index(self) -> None:
        self.index.build_name_to_id_index(
            {v["name"]: k for k, v in self.raw.items() if "name" in v},
        )

    def build_content(self) -> None:
        assert self._raw_
        self.index.build_content(
            self._raw_,
        )

    def check_out_of_date(self) -> bool:
        index = self.index
        if not index.content.exists():
            return True
        assert self._raw_
        content_raw = index.content.read_bytes()
        md5_1 = hashlib.md5(content_raw).hexdigest()
        md5_2 = hashlib.md5(self._raw_).hexdigest()
        return md5_1 != md5_2

    async def build_index(self) -> None:
        await self.init_raw()
        if self.check_out_of_date():
            logger.info(f"{self.category} 已过期或不存在，正在构建")
            logger.info(f"构建 {self.category} 名称 index (语言: {self.lang})")
            self.build_name_to_id_index()
            logger.info(f"构建 {self.category} 内容 index (语言: {self.lang})")
            self.build_content()
        else:
            logger.info(f"index {self.category} (语言: {self.lang}) 无变化")

    @staticmethod
    async def run_build(*categories: str) -> None:
        for category in categories:
            await asyncio.gather(
                *[Builder(category, lang).build_index() for lang in LANG],
            )
