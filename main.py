from __future__ import annotations

import sys

from herta.bot import init_bot, run
from herta.config import Setting
from herta.log import logger

try:
    config = Setting(_env_file=(".env", ".env.prod", ".env.dev"))
    if not config.bot_id and not config.bot_secret:
        raise ValueError("bot_id 或 config 为空")  # noqa: TRY301
except ValueError as e:
    logger.critical("Herta 启动失败:配置项出错")
    logger.exception(str(e))
    sys.exit(1)

init_bot(config.bot_id, config.bot_secret)
logger.success("初始化机器人完成")


if __name__ == "__main__":
    run(config.host, config.port)
