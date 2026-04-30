"""文档解析和分片测试脚本"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.document_parser.parser_factory import ParserFactory
from src.core.chunker.sentence_chunker import DocumentChunker
from src.core.chunker.metadata_binder import MetadataBinder
from src.utils.logger import logger


def test_text_parsing():
    """测试文本解析和分片"""
    print("=" * 50)
    print("测试文本解析和分片")
    print("=" * 50)

    # 创建测试文件
    test_content = """# Python编程基础

## 第一章 变量和数据类型

Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。

变量是存储数据的容器。在Python中，变量不需要声明类型，可以直接赋值。

## 第二章 控制流程

条件语句用于根据条件执行不同的代码块。

循环语句用于重复执行一段代码。Python支持for循环和while循环。

## 第三章 函数

函数是组织好的、可重复使用的、用来实现单一或相关联功能的代码段。

定义函数使用def关键字。"""

    # 写入测试文件
    test_file = PROJECT_ROOT / "data" / "raw_documents" / "test.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)

    # 解析文档
    doc = ParserFactory.parse(test_file)
    print(f"解析结果:")
    print(f"  - 文档名称: {doc.doc_name}")
    print(f"  - 文档类型: {doc.doc_type}")
    print(f"  - 标题: {doc.title}")
    print(f"  - 页数/章节数: {doc.page_count}")
    print(f"  - 内容长度: {len(doc.content)}字符")
    print(f"  - 解析状态: {'成功' if doc.parse_success else '失败'}")

    # 分片
    chunker = DocumentChunker()
    chunks = chunker.chunk_document(
        content=doc.content,
        pages=doc.pages,
        doc_id=doc.doc_id,
        doc_name=doc.doc_name,
        doc_type=doc.doc_type,
        title=doc.title,
    )

    print(f"\n分片结果:")
    print(f"  - 分片数量: {len(chunks)}")
    for i, chunk in enumerate(chunks[:3]):  # 只显示前3个
        print(f"  - 分片{i}: {chunk.content[:60]}...")

    # 绑定元数据
    binder = MetadataBinder()
    chunks = binder.bind_course_metadata(
        chunks=chunks,
        course_name="Python编程基础",
        chapter="第一章",
        tags=["编程", "Python", "入门"],
    )

    print(f"\n元数据绑定后:")
    print(f"  - 课程名称: {chunks[0].metadata.course_name}")
    print(f"  - 标签: {chunks[0].metadata.tags}")

    # 清理测试文件
    test_file.unlink()

    print("\n文本解析测试通过!")
    return True


def test_document_chunker():
    """测试文档分片器"""
    print("\n" + "=" * 50)
    print("测试文档分片器")
    print("=" * 50)

    # 模拟多页内容
    pages = [
        "第一页：Python简介。Python是一种通用编程语言。",
        "第二页：变量定义。变量是存储数据的容器。",
        "第三页：数据类型。Python支持多种数据类型。",
    ]

    chunker = DocumentChunker()
    chunks = chunker.chunk_document(
        content="\n".join(pages),
        pages=pages,
        doc_id="test_doc",
        doc_name="python_intro.pdf",
        doc_type="pdf",
    )

    print(f"分片数量: {len(chunks)}")
    for chunk in chunks:
        print(f"  - 页{chunk.metadata.page_number}: {chunk.content[:40]}...")

    print("\n文档分片测试通过!")
    return True


def main():
    """主测试函数"""
    logger.info("开始测试文档解析和分片功能")

    try:
        # 测试文本解析
        if not test_text_parsing():
            logger.error("文本解析测试失败")
            return False

        # 测试文档分片
        if not test_document_chunker():
            logger.error("文档分片测试失败")
            return False

        logger.info("所有测试通过!")
        return True

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
