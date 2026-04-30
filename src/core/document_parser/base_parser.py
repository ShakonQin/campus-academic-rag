"""文档解析器基类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from datetime import datetime


@dataclass
class ParsedDocument:
    """解析后的文档数据结构"""

    # 文档元数据
    doc_id: str = ""
    doc_name: str = ""
    doc_type: str = ""  # pdf, pptx, docx, md, txt
    doc_path: str = ""

    # 文档内容
    content: str = ""  # 完整文本内容
    pages: List[str] = field(default_factory=list)  # 按页/幻灯片分割的内容

    # 元数据
    author: str = ""
    title: str = ""
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    page_count: int = 0

    # 额外元数据（用于检索过滤）
    course_name: str = ""  # 课程名称
    chapter: str = ""  # 章节
    section: str = ""  # 小节
    tags: List[str] = field(default_factory=list)  # 标签

    # 处理信息
    parsed_at: datetime = field(default_factory=datetime.now)
    parse_success: bool = True
    error_message: str = ""


class BaseParser(ABC):
    """文档解析器基类"""

    SUPPORTED_EXTENSIONS: List[str] = []

    def __init__(self):
        """初始化解析器"""
        pass

    @abstractmethod
    def parse(self, file_path: Path) -> ParsedDocument:
        """解析文档

        Args:
            file_path: 文档文件路径

        Returns:
            解析后的文档对象
        """
        pass

    def validate_file(self, file_path: Path) -> bool:
        """验证文件是否有效

        Args:
            file_path: 文件路径

        Returns:
            文件是否有效
        """
        if not file_path.exists():
            return False
        if not file_path.is_file():
            return False
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            return False
        return True

    def _create_error_document(self, file_path: Path, error_msg: str) -> ParsedDocument:
        """创建错误文档对象

        Args:
            file_path: 文件路径
            error_msg: 错误信息

        Returns:
            错误文档对象
        """
        return ParsedDocument(
            doc_id=str(file_path.stem),
            doc_name=file_path.name,
            doc_type=file_path.suffix.lower().lstrip("."),
            doc_path=str(file_path),
            parse_success=False,
            error_message=error_msg,
        )

    def _extract_metadata(self, file_path: Path) -> dict:
        """提取文件基础元数据

        Args:
            file_path: 文件路径

        Returns:
            元数据字典
        """
        stat = file_path.stat()
        return {
            "doc_id": str(file_path.stem),
            "doc_name": file_path.name,
            "doc_type": file_path.suffix.lower().lstrip("."),
            "doc_path": str(file_path),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
        }
