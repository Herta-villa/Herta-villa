from __future__ import annotations

import contextlib

from herta.bot import get_bot
from herta.exception import UploadFailed
from herta.log import logger
from herta.utils.cache import Cache
from herta.utils.index.build_index import Builder
from herta.utils.index.index import Index
from herta.utils.resource import sr_res

from hertavilla import (
    Image,
    MessageChain,
    RegexResult,
    SendMessageEvent,
    VillaBot,
    get_backend,
)
from hertavilla.exception import CallingApiException

backend = get_backend()
char_cache = Cache("character_guide")
light_cone_cache = Cache("light_cone_guide")
relic_sets_cache = Cache("relic_set_guide")

bot = get_bot()


@backend.on_startup
async def build_index() -> None:
    await Builder.run_build("characters", "light_cones", "relic_sets")


char_index = Index("characters")
light_cones_index = Index("light_cones")
relic_sets_index = Index("relic_sets")

CHAR_SEARCH = ("角色", char_index, char_cache, 1920, 3000)
LIGHT_CONE_SEARCH = ("光锥", light_cones_index, light_cone_cache, 1920, 1080)
RELIC_SEARCH = ("遗器", relic_sets_index, relic_sets_cache, 1800, 720)


async def _img_cache(
    bot: VillaBot,
    villa_id: int,
    path: str,
    cache: Cache,
) -> str:
    if cache[path]:
        return cache[path]
    for i in range(4):
        if i > 0:
            logger.warning(f"上传图片失败，正在重试 {i}/3")
        with contextlib.suppress(CallingApiException):
            img = cache[path] = await bot.transfer_image(
                villa_id,
                sr_res(f"/{path}"),
            )
            return img
    raise UploadFailed


async def _get_guide(name: str, bot: VillaBot, villa_id: int) -> Image | None:
    for search in (CHAR_SEARCH, LIGHT_CONE_SEARCH, RELIC_SEARCH):
        category, index, cache, width, height = search
        logger.opt(colors=True).info(
            f"正在 <y>{category}</y> 中搜索 <green>{name}</green>...",
        )
        with contextlib.suppress(ValueError):
            index.set_id_by_name(name)
            logger.opt(colors=True).success(
                f"已在 <y>{category}</y> 中找到 <green>{name}</green>",
            )
            path = index["guide_overview"][0]  # 听语惊花
            return Image(
                await _img_cache(bot, villa_id, path, cache),
                width,
                height,
            )
    return None


@bot.regex(r"/星穹攻略 (.+)")
async def _(event: SendMessageEvent, bot: VillaBot, match_result: RegexResult):
    name = match_result.re_match[1]
    try:
        msg = (
            await _get_guide(name[1], bot, event.villa_id)
            or "未找到相关内容，请检查是否输入有误~"
        )
    except UploadFailed:
        msg = "出现错误: 图片上传失败。请重试"
    chain = MessageChain(msg)
    await bot.send(event.villa_id, event.room_id, chain)
