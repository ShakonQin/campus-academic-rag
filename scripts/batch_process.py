"""批量文档处理脚本"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.logger import logger


def process_documents(input_dir: str, output_dir: str = None) -> None:
    """批量处理文档

    Args:
        input_dir: 输入文档目录
        output_dir: 输出目录（可选）
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"输入目录不存在: {input_path}")
        return

    # 支持的文件格式
    supported_formats = {".pdf", ".pptx", ".ppt", ".docx", ".doc", ".md", ".txt"}

    # 收集所有文档
    documents = []
    for ext in supported_formats:
        documents.extend(input_path.glob(f"*{ext}"))
        documents.extend(input_path.glob(f"**/*{ext}"))

    logger.info(f"找到 {len(documents)} 个文档待处理")

    if not documents:
        logger.warning("未找到支持格式的文档")
        return

    # TODO: 实现文档处理逻辑（步骤2完成）
    logger.info("文档处理功能将在步骤2实现")


def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(description="批量文档处理脚本")
    parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="输入文档目录路径"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="输出目录路径（可选）"
    )

    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("批量文档处理")
    logger.info("=" * 50)

    process_documents(args.input, args.output)

    logger.info("=" * 50)
    logger.info("处理完成")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
