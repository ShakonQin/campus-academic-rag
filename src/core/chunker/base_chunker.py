"""分片器基类和数据结构"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ChunkMetadata:
    """分片元数据"""

    # 文档来源
    doc_id: str = ""
    doc_name: str = ""
    doc_type: str = ""
    doc_path: str = ""

    # 位置信息
    page_number: int = 0  # 页码/幻灯片编号
    chunk_index: int = 0  # 在文档中的分片序号
    start_char: int = 0  # 起始字符位置
    end_char: int = 0  # 结束字符位置

    # 文档结构信息
    chapter: str = ""  # 章节
    section: str = ""  # 小节
    title: str = ""  # 标题

    # 内容类型标记
    content_type: str = "text"  # text, formula, table, figure, code
    has_formula: bool = False
    has_table: bool = False
    has_figure: bool = False

    # 文档元数据
    author: str = ""
    course_name: str = ""
    tags: List[str] = field(default_factory=list)

    # 时间信息
    created_at: Optional[datetime] = None
    chunked_at: datetime = field(default_factory=datetime.now)


@dataclass
class Chunk:
    """文档分片"""

    # 分片内容
    chunk_id: str = ""  # 唯一标识
    content: str = ""  # 分片文本内容

    # 元数据
    metadata: ChunkMetadata = field(default_factory=ChunkMetadata)

    # 嵌入向量（后续填充）
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "metadata": {
                "doc_id": self.metadata.doc_id,
                "doc_name": self.metadata.doc_name,
                "doc_type": self.metadata.doc_type,
                "doc_path": self.metadata.doc_path,
                "page_number": self.metadata.page_number,
                "chunk_index": self.metadata.chunk_index,
                "chapter": self.metadata.chapter,
                "section": self.metadata.section,
                "title": self.metadata.title,
                "content_type": self.metadata.content_type,
                "has_formula": self.metadata.has_formula,
                "has_table": self.metadata.has_table,
                "has_figure": self.metadata.has_figure,
                "author": self.metadata.author,
                "course_name": self.metadata.course_name,
                "tags": self.metadata.tags,
            },
        }


class BaseChunker(ABC):
    """分片器基类"""

    @abstractmethod
    def chunk(self, content: str, metadata: Optional[ChunkMetadata] = None) -> List[Chunk]:
        """对内容进行分片

        Args:
            content: 文本内容
            metadata: 基础元数据（可选）

        Returns:
            分片列表
        """
        pass

    def _generate_chunk_id(self, doc_id: str, chunk_index: int) -> str:
        """生成分片ID

        Args:
            doc_id: 文档ID
            chunk_index: 分片序号

        Returns:
            分片ID
        """
        return f"{doc_id}_chunk_{chunk_index:04d}"

    def _create_chunk(
        self,
        content: str,
        doc_id: str,
        chunk_index: int,
        base_metadata: Optional[ChunkMetadata] = None,
        **kwargs,
    ) -> Chunk:
        """创建分片对象

        Args:
            content: 分片内容
            doc_id: 文档ID
            chunk_index: 分片序号
            base_metadata: 基础元数据
            **kwargs: 额外元数据

        Returns:
            分片对象
        """
        # 创建元数据
        metadata = ChunkMetadata()
        if base_metadata:
            metadata = ChunkMetadata(
                doc_id=base_metadata.doc_id,
                doc_name=base_metadata.doc_name,
                doc_type=base_metadata.doc_type,
                doc_path=base_metadata.doc_path,
                page_number=base_metadata.page_number,
                chapter=base_metadata.chapter,
                section=base_metadata.section,
                title=base_metadata.title,
                author=base_metadata.author,
                course_name=base_metadata.course_name,
                tags=base_metadata.tags.copy() if base_metadata.tags else [],
                created_at=base_metadata.created_at,
            )

        # 更新分片特定信息
        metadata.chunk_index = chunk_index
        metadata.start_char = kwargs.get("start_char", 0)
        metadata.end_char = kwargs.get("end_char", len(content))
        metadata.content_type = kwargs.get("content_type", "text")

        # 检测内容类型
        metadata.has_formula = self._detect_formula(content)
        metadata.has_table = self._detect_table(content)
        metadata.has_figure = self._detect_figure(content)

        return Chunk(
            chunk_id=self._generate_chunk_id(doc_id, chunk_index),
            content=content,
            metadata=metadata,
        )

    def _detect_formula(self, content: str) -> bool:
        """检测是否包含公式

        Args:
            content: 文本内容

        Returns:
            是否包含公式
        """
        import re
        # 检测LaTeX公式标记
        formula_patterns = [
            r"\$.*?\$",  # 行内公式
            r"\$\$.*?\$\$",  # 块级公式
            r"\\[a-zA-Z]+",  # LaTeX命令
            r"\\frac|\\sum|\\int|\\prod",  # 常见公式命令
        ]
        for pattern in formula_patterns:
            if re.search(pattern, content, re.DOTALL):
                return True
        return False

    def _detect_table(self, content: str) -> bool:
        """检测是否包含表格

        Args:
            content: 文本内容

        Returns:
            是否包含表格
        """
        # 检测表格标记
        table_indicators = ["|", "┌", "┐", "└", "┘", "─", "│"]
        lines = content.split("\n")
        table_line_count = sum(
            1 for line in lines if any(indicator in line for indicator in table_indicators)
        )
        return table_line_count >= 2

    def _detect_figure(self, content: str) -> bool:
        """检测是否包含图表说明

        Args:
            content: 文本内容

        Returns:
            是否包含图表
        """
        import re
        figure_patterns = [
            r"图\s*\d+",  # 图1, 图2
            r"Figure\s*\d+",  # Figure 1
            r"Fig\.\s*\d+",  # Fig. 1
            r"表\s*\d+",  # 表1
            r"Table\s*\d+",  # Table 1
        ]
        for pattern in figure_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
