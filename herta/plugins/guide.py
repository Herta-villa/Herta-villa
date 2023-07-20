from __future__ import annotations

import re

from herta.bot import get_bot
from herta.utils.cache import Cache
from herta.utils.index.build_index import Builder
from herta.utils.index.index import Index
from herta.utils.resource import sr_res

from hertavilla import (
    Image,
    MessageChain,
    SendMessageEvent,
    VillaBot,
    get_backend,
)

backend = get_backend()
char_cache = Cache("character_guide")


bot = get_bot()
regex = r"/星穹攻略 (.+)"


@backend.on_startup
async def build_index() -> None:
    await Builder.run_build("characters")


index = Index("characters")


@bot.regex(regex)
async def _(event: SendMessageEvent, bot: VillaBot):
    name = re.match(regex, event.message.plaintext)
    if not name:
        return
    chain = MessageChain()
    try:
        index.set_id_by_name(name[1])
    except ValueError:
        chain.append("没找到角色攻略，是不是你名称输错了呢~")
    else:
        path = index["guide_overview"][0]  # Nwflower
        if char_cache[path]:
            img = char_cache[path]
        else:
            img = char_cache[path] = await bot.transfer_image(
                event.villa_id,
                sr_res(f"/{path}"),
            )
        chain.append(Image(img, width=1920, height=3000))
    await bot.send(event.villa_id, event.room_id, chain)
