"""项目初始化脚本"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.logger import logger
from src.config.settings import settings


def init_directories() -> None:
    """创建必要的目录结构"""
    directories = [
        "data/raw_documents",
        "data/processed_chunks",
        "data/vector_index",
        "logs",
        "models",
    ]

    for dir_path in directories:
        full_path = PROJECT_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"目录已创建/确认: {full_path}")


def check_env_file() -> None:
    """检查环境变量文件"""
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"

    if not env_file.exists():
        if env_example.exists():
            logger.warning(".env文件不存在，请复制.env.example并填入配置")
            logger.info("命令: cp .env.example .env")
        else:
            logger.error(".env.example文件不存在，请检查项目完整性")
    else:
        logger.info(".env文件已存在")


def check_dependencies() -> None:
    """检查核心依赖"""
    try:
        import pdfplumber
        logger.info("pdfplumber: OK")
    except ImportError:
        logger.warning("pdfplumber: 未安装")

    try:
        import sentence_transformers
        logger.info("sentence_transformers: OK")
    except ImportError:
        logger.warning("sentence_transformers: 未安装")

    try:
        import chromadb
        logger.info("chromadb: OK")
    except ImportError:
        logger.warning("chromadb: 未安装")

    try:
        import fastapi
        logger.info("fastapi: OK")
    except ImportError:
        logger.warning("fastapi: 未安装")


def main() -> None:
    """主函数"""
    logger.info("=" * 50)
    logger.info("校园学术智能RAG检索系统 - 项目初始化")
    logger.info(f"版本: {settings.app.app_version}")
    logger.info("=" * 50)

    # 初始化目录
    init_directories()

    # 检查环境变量
    check_env_file()

    # 检查依赖
    check_dependencies()

    logger.info("=" * 50)
    logger.info("项目初始化完成！")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
