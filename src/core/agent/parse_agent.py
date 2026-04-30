"""文档解析专家Agent"""

import time
from pathlib import Path
from typing import Dict, Any, List

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.core.document_parser.parser_factory import ParserFactory
from src.core.chunker.sentence_chunker import DocumentChunker
from src.core.chunker.metadata_binder import MetadataBinder
from src.utils.logger import logger


class ParseAgent(BaseAgent):
    """文档解析专家Agent

    负责各类校园文档的结构化解析、格式处理、分片处理。
    """

    AGENT_TYPE = AgentType.PARSE

    def __init__(self):
        """初始化解析Agent"""
        super().__init__()
        self.parser_factory = ParserFactory
        self.chunker = DocumentChunker()
        self.metadata_binder = MetadataBinder()

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行文档解析任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            解析结果响应
        """
        start_time = time.time()

        try:
            doc_path = context.doc_path
            if not doc_path:
                return self._create_error_response("文档路径为空")

            path = Path(doc_path)
            if not path.exists():
                return self._create_error_response(f"文档不存在: {doc_path}")

            # 解析文档
            parsed_doc = self.parser_factory.parse(path)
            if not parsed_doc.parse_success:
                return self._create_error_response(f"文档解析失败: {parsed_doc.error_message}")

            # 分片
            chunks = self.chunker.chunk_document(
                content=parsed_doc.content,
                pages=parsed_doc.pages,
                doc_id=parsed_doc.doc_id,
                doc_name=parsed_doc.doc_name,
                doc_type=parsed_doc.doc_type,
                doc_path=parsed_doc.doc_path,
                author=parsed_doc.author,
                title=parsed_doc.title,
            )

            # 绑定额外元数据
            if context.metadata.get("course_name"):
                chunks = self.metadata_binder.bind_course_metadata(
                    chunks=chunks,
                    course_name=context.metadata["course_name"],
                    chapter=context.metadata.get("chapter", ""),
                    tags=context.metadata.get("tags", []),
                )

            # 转换为字典格式
            chunks_data = [chunk.to_dict() for chunk in chunks]

            execution_time = time.time() - start_time

            return self._create_success_response(
                data={
                    "doc_id": parsed_doc.doc_id,
                    "doc_name": parsed_doc.doc_name,
                    "doc_type": parsed_doc.doc_type,
                    "page_count": parsed_doc.page_count,
                    "chunks_count": len(chunks),
                    "chunks": chunks_data,
                },
                message=f"文档解析完成: {parsed_doc.doc_name}, {len(chunks)}个分片",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"解析Agent执行失败: {e}")
            return self._create_error_response(str(e), execution_time)

    def parse_and_index(
        self,
        doc_path: str,
        retrieval_engine,
        **kwargs,
    ) -> Dict[str, Any]:
        """解析文档并构建索引

        Args:
            doc_path: 文档路径
            retrieval_engine: 检索引擎
            **kwargs: 额外参数

        Returns:
            处理结果
        """
        # 创建上下文
        context = AgentContext(
            doc_path=doc_path,
            metadata=kwargs,
        )

        # 执行解析
        response = self.execute(context)

        if not response.success:
            return {"success": False, "error": response.error}

        # 获取分片数据
        chunks_data = response.data.get("chunks", [])

        # 构建索引
        from src.core.chunker.base_chunker import Chunk, ChunkMetadata

        chunks = []
        for chunk_data in chunks_data:
            metadata = ChunkMetadata(**chunk_data["metadata"])
            chunk = Chunk(
                chunk_id=chunk_data["chunk_id"],
                content=chunk_data["content"],
                metadata=metadata,
            )
            chunks.append(chunk)

        retrieval_engine.build_indexes(chunks)

        return {
            "success": True,
            "doc_id": response.data["doc_id"],
            "doc_name": response.data["doc_name"],
            "chunks_count": response.data["chunks_count"],
        }
