from __future__ import annotations

import importlib
from pathlib import Path
from pkgutil import iter_modules
import sys

from herta.bot import init_bot, run
from herta.config import Setting
from herta.log import logger

try:
    config = Setting(_env_file=(".env", ".env.prod", ".env.dev"))
    if not config.bot_id and not config.bot_secret and not config.bot_pub_key:
        raise ValueError("bot_id 或 config 为空")  # noqa: TRY301
except ValueError as e:
    logger.critical("Herta 启动失败:配置项出错")
    logger.exception(str(e))
    sys.exit(1)
init_bot(config.bot_id, config.bot_secret, config.bot_pub_key)
logger.success("初始化机器人完成")
for module_info in iter_modules(
    [str(Path(__file__).parent / "herta" / "plugins")],
):
    if not (name := module_info.name).startswith("_"):
        logger.info(f"加载插件: {name}")
        importlib.import_module(f"herta.plugins.{name}")
logger.success("加载插件完成")


if __name__ == "__main__":
    run(config.host, config.port)
