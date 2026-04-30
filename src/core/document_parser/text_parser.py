"""Markdown和纯文本文档解析器"""

from pathlib import Path
from typing import List

from src.core.document_parser.base_parser import BaseParser, ParsedDocument
from src.utils.logger import logger


class TextParser(BaseParser):
    """纯文本文档解析器

    支持解析.txt格式文档。
    """

    SUPPORTED_EXTENSIONS = [".txt"]

    def parse(self, file_path: Path) -> ParsedDocument:
        """解析纯文本文档

        Args:
            file_path: 文本文件路径

        Returns:
            解析后的文档对象
        """
        if not self.validate_file(file_path):
            return self._create_error_document(file_path, "文件验证失败")

        try:
            # 提取基础元数据
            metadata = self._extract_metadata(file_path)

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 按段落分割
            paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

            # 创建文档对象
            doc = ParsedDocument(
                doc_id=metadata["doc_id"],
                doc_name=metadata["doc_name"],
                doc_type="txt",
                doc_path=metadata["doc_path"],
                content=content,
                pages=paragraphs,
                author=metadata.get("author", ""),
                title=metadata.get("title", metadata["doc_name"]),
                created_at=metadata.get("created_at"),
                modified_at=metadata.get("modified_at"),
                page_count=len(paragraphs),
                parse_success=True,
            )

            logger.info(f"文本解析成功: {file_path.name}, 共{len(paragraphs)}段")
            return doc

        except Exception as e:
            logger.error(f"文本解析失败: {file_path.name}, 错误: {e}")
            return self._create_error_document(file_path, str(e))


class MarkdownParser(BaseParser):
    """Markdown文档解析器

    支持解析.md格式文档，保留标题结构。
    """

    SUPPORTED_EXTENSIONS = [".md", ".markdown"]

    def parse(self, file_path: Path) -> ParsedDocument:
        """解析Markdown文档

        Args:
            file_path: Markdown文件路径

        Returns:
            解析后的文档对象
        """
        if not self.validate_file(file_path):
            return self._create_error_document(file_path, "文件验证失败")

        try:
            # 提取基础元数据
            metadata = self._extract_metadata(file_path)

            # 读取文件内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 按标题分割为章节
            sections = self._split_by_headers(content)

            # 创建文档对象
            doc = ParsedDocument(
                doc_id=metadata["doc_id"],
                doc_name=metadata["doc_name"],
                doc_type="md",
                doc_path=metadata["doc_path"],
                content=content,
                pages=sections,
                author=metadata.get("author", ""),
                title=self._extract_title(content) or metadata["doc_name"],
                created_at=metadata.get("created_at"),
                modified_at=metadata.get("modified_at"),
                page_count=len(sections),
                parse_success=True,
            )

            logger.info(f"Markdown解析成功: {file_path.name}, 共{len(sections)}章节")
            return doc

        except Exception as e:
            logger.error(f"Markdown解析失败: {file_path.name}, 错误: {e}")
            return self._create_error_document(file_path, str(e))

    def _split_by_headers(self, content: str) -> List[str]:
        """按标题分割Markdown内容

        Args:
            content: Markdown内容

        Returns:
            章节列表
        """
        import re

        # 匹配Markdown标题
        header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

        sections = []
        current_pos = 0

        for match in header_pattern.finditer(content):
            # 保存标题之前的内容
            if match.start() > current_pos:
                section = content[current_pos:match.start()].strip()
                if section:
                    sections.append(section)

            # 更新当前位置
            current_pos = match.start()

        # 保存最后一部分
        if current_pos < len(content):
            section = content[current_pos:].strip()
            if section:
                sections.append(section)

        return sections

    def _extract_title(self, content: str) -> str:
        """提取Markdown标题

        Args:
            content: Markdown内容

        Returns:
            标题文本
        """
        import re

        # 匹配第一个一级标题
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        return ""
