"""日志工具模块"""

import sys
from pathlib import Path
from loguru import logger

from src.config.settings import settings


def setup_logger() -> None:
    """配置日志系统"""
    # 移除默认handler
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.app.log_level,
        colorize=True,
    )

    # 文件输出
    log_file = Path(settings.app.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
               "{name}:{function}:{line} | {message}",
        level=settings.app.log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )


# 初始化日志
setup_logger()
