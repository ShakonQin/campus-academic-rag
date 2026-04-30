"""全流程测试脚本"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.document_parser.parser_factory import ParserFactory
from src.core.chunker.sentence_chunker import DocumentChunker
from src.core.retriever.retrieval_engine import RetrievalEngine
from src.core.agent import (
    AgentRouter, AgentContext, AgentType,
    ParseAgent, RetrieveAgent, GenerateAgent, VerifyAgent
)
from src.core.generator import ResponseGenerator, CitationTracker
from src.utils.logger import logger


def create_test_document():
    """创建测试文档"""
    test_content = """# Python编程基础教程

## 第一章 Python简介

Python是一种解释型、面向对象、动态数据类型的高级程序设计语言。由Guido van Rossum于1991年创建。

Python的特点：
1. 简单易学：语法简洁清晰
2. 开源免费：拥有庞大的社区
3. 跨平台：支持Windows、Linux、MacOS
4. 丰富的库：拥有大量的标准库和第三方库

## 第二章 变量和数据类型

变量是存储数据的容器。在Python中，变量不需要声明类型，可以直接赋值。

基本数据类型包括：
- 整数（int）：如 1, 2, 3
- 浮点数（float）：如 3.14, 2.5
- 字符串（str）：如 "Hello, World!"
- 布尔值（bool）：True 或 False

## 第三章 控制流程

条件语句用于根据条件执行不同的代码块：

```python
if condition:
    # 执行代码
elif other_condition:
    # 执行其他代码
else:
    # 默认执行
```

循环语句用于重复执行代码：

```python
for i in range(10):
    print(i)

while condition:
    # 循环体
```
"""

    test_file = PROJECT_ROOT / "data" / "raw_documents" / "python_tutorial.md"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(test_content)

    return test_file


def test_document_parsing():
    """测试文档解析"""
    print("=" * 50)
    print("测试1: 文档解析")
    print("=" * 50)

    # 创建测试文档
    test_file = create_test_document()

    # 解析文档
    doc = ParserFactory.parse(test_file)
    print(f"解析结果:")
    print(f"  - 文档名称: {doc.doc_name}")
    print(f"  - 标题: {doc.title}")
    print(f"  - 页数: {doc.page_count}")
    print(f"  - 内容长度: {len(doc.content)}字符")
    print(f"  - 状态: {'成功' if doc.parse_success else '失败'}")

    # 分片
    chunker = DocumentChunker()
    chunks = chunker.chunk_document(
        content=doc.content,
        pages=doc.pages,
        doc_id=doc.doc_id,
        doc_name=doc.doc_name,
        doc_type=doc.doc_type,
    )

    print(f"  - 分片数量: {len(chunks)}")

    # 清理
    test_file.unlink()

    return chunks


def test_retrieval(chunks):
    """测试检索功能"""
    print("\n" + "=" * 50)
    print("测试2: 检索功能")
    print("=" * 50)

    # 使用mock嵌入模型（避免网络下载）
    import numpy as np
    from unittest.mock import MagicMock

    mock_embedding = MagicMock()
    def mock_encode(texts, **kwargs):
        if isinstance(texts, str):
            return np.random.rand(768).tolist()
        return [np.random.rand(768).tolist() for _ in texts]
    mock_embedding.encode = mock_encode

    # 创建检索引擎
    from src.core.embedding.index_builder import VectorIndexBuilder
    vector_index = VectorIndexBuilder(embedding=mock_embedding)
    engine = RetrievalEngine()

    # 构建索引
    # 构建BM25索引
    engine.keyword_retriever.build_index(chunks)
    print("BM25索引构建完成")

    # 测试查询
    queries = [
        "什么是Python？",
        "Python有哪些数据类型？",
        "如何使用条件语句？",
    ]

    for query in queries:
        print(f"\n查询: {query}")
        results = engine.retrieve(query, top_k=3, use_vector=False, use_reranker=False)
        print(f"返回 {len(results)} 个结果")
        for i, r in enumerate(results[:2], 1):
            print(f"  {i}. {r.content[:50]}... (分数: {r.final_score:.3f})")

    return engine


def test_agent_pipeline(engine):
    """测试Agent管道"""
    print("\n" + "=" * 50)
    print("测试3: Agent管道")
    print("=" * 50)

    # 创建Agent
    retrieve_agent = RetrieveAgent(engine)
    verify_agent = VerifyAgent()

    # 创建上下文
    context = AgentContext(query="Python有哪些特点？")

    # 执行检索
    print("执行检索Agent...")
    retrieve_response = retrieve_agent.execute(context)
    if retrieve_response.success:
        context.retrieval_results = retrieve_response.data["results"]
        print(f"检索成功: {len(context.retrieval_results)}个结果")

    # 执行校验
    context.generated_answer = "Python是一种简单易学的编程语言，具有开源免费、跨平台等特点。"
    print("执行校验Agent...")
    verify_response = verify_agent.execute(context)
    if verify_response.success:
        verification = verify_response.data["verification"]
        print(f"校验完成: 可信度={verification['confidence']:.1%}")

    return context


def test_citation_tracking():
    """测试引用追踪"""
    print("\n" + "=" * 50)
    print("测试4: 引用追踪")
    print("=" * 50)

    from src.core.retriever.multi_way_merge import RetrievalResult

    # 创建模拟结果
    results = [
        RetrievalResult(
            chunk_id="chunk_1",
            content="Python是一种解释型语言",
            metadata={"doc_name": "python.pdf", "page_number": 1},
            scores={"vector": 0.9},
            final_score=0.9,
        ),
    ]

    # 测试引用追踪
    tracker = CitationTracker()
    citations = tracker.track_retrieval(results)

    print(f"引用数量: {len(citations)}")
    for c in citations:
        print(f"  - [{c.citation_id}] {c.doc_name} p.{c.page_number}")

    # 生成参考文献
    bib = tracker.generate_bibliography()
    print(f"\n{bib}")


def main():
    """主测试函数"""
    logger.info("=" * 60)
    logger.info("校园学术智能RAG检索系统 - 全流程测试")
    logger.info("=" * 60)

    try:
        # 测试文档解析
        chunks = test_document_parsing()
        if not chunks:
            logger.error("文档解析测试失败")
            return False

        # 测试检索
        engine = test_retrieval(chunks)
        if not engine:
            logger.error("检索测试失败")
            return False

        # 测试Agent管道
        test_agent_pipeline(engine)

        # 测试引用追踪
        test_citation_tracking()

        logger.info("=" * 60)
        logger.info("所有测试通过！MVP功能验证完成")
        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
