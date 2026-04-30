"""引用溯源工具"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from src.core.retriever.multi_way_merge import RetrievalResult
from src.utils.logger import logger


@dataclass
class Citation:
    """引用信息"""
    citation_id: str = ""
    doc_id: str = ""
    doc_name: str = ""
    doc_type: str = ""
    page_number: int = 0
    chunk_id: str = ""
    content_snippet: str = ""  # 内容片段
    relevance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "citation_id": self.citation_id,
            "doc_id": self.doc_id,
            "doc_name": self.doc_name,
            "doc_type": self.doc_type,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "content_snippet": self.content_snippet[:200],  # 限制长度
            "relevance_score": self.relevance_score,
        }

    def format(self, style: str = "default") -> str:
        """格式化引用

        Args:
            style: 格式风格（default/apa/mla）

        Returns:
            格式化后的引用文本
        """
        if style == "apa":
            return f"{self.doc_name} (p. {self.page_number})"
        elif style == "mla":
            return f"{self.doc_name}, p. {self.page_number}"
        else:
            if self.page_number:
                return f"{self.doc_name}, 第{self.page_number}页"
            return self.doc_name


class CitationTracker:
    """引用追踪器

    追踪和管理回答中的引用信息。
    """

    def __init__(self):
        """初始化引用追踪器"""
        self._citations: List[Citation] = []
        self._citation_counter = 0

    def track_retrieval(self, retrieval_results: List[RetrievalResult]) -> List[Citation]:
        """追踪检索结果的引用

        Args:
            retrieval_results: 检索结果

        Returns:
            引用列表
        """
        citations = []
        for result in retrieval_results:
            citation = self._create_citation(result)
            citations.append(citation)

        self._citations = citations
        return citations

    def _create_citation(self, result: RetrievalResult) -> Citation:
        """创建引用

        Args:
            result: 检索结果

        Returns:
            引用对象
        """
        self._citation_counter += 1

        metadata = result.metadata
        content = result.content

        # 提取内容片段（前200字符）
        snippet = content[:200] + "..." if len(content) > 200 else content

        return Citation(
            citation_id=f"cite_{self._citation_counter}",
            doc_id=metadata.get("doc_id", ""),
            doc_name=metadata.get("doc_name", ""),
            doc_type=metadata.get("doc_type", ""),
            page_number=metadata.get("page_number", 0),
            chunk_id=result.chunk_id,
            content_snippet=snippet,
            relevance_score=result.final_score,
        )

    def get_citations(self) -> List[Citation]:
        """获取所有引用

        Returns:
            引用列表
        """
        return self._citations

    def get_citation_by_doc(self, doc_name: str) -> List[Citation]:
        """按文档名称获取引用

        Args:
            doc_name: 文档名称

        Returns:
            引用列表
        """
        return [c for c in self._citations if c.doc_name == doc_name]

    def format_citations(self, style: str = "default") -> str:
        """格式化所有引用

        Args:
            style: 格式风格

        Returns:
            格式化后的引用文本
        """
        if not self._citations:
            return ""

        formatted = []
        for i, citation in enumerate(self._citations, 1):
            formatted.append(f"[{i}] {citation.format(style)}")

        return "\n".join(formatted)

    def generate_bibliography(self) -> str:
        """生成参考文献列表

        Returns:
            参考文献文本
        """
        if not self._citations:
            return ""

        # 按文档去重
        unique_docs = {}
        for citation in self._citations:
            if citation.doc_name not in unique_docs:
                unique_docs[citation.doc_name] = citation

        bibliography = ["参考文献:"]
        for i, (doc_name, citation) in enumerate(unique_docs.items(), 1):
            entry = f"[{i}] {citation.doc_name}"
            if citation.doc_type:
                entry += f" ({citation.doc_type})"
            bibliography.append(entry)

        return "\n".join(bibliography)

    def clear(self) -> None:
        """清空引用"""
        self._citations.clear()
        self._citation_counter = 0
