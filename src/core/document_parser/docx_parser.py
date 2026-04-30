"""Word文档解析器"""

from pathlib import Path
from typing import List

from docx import Document
from docx.document import Document as DocumentType

from src.core.document_parser.base_parser import BaseParser, ParsedDocument
from src.utils.logger import logger


class DOCXParser(BaseParser):
    """Word文档解析器

    支持解析DOCX文档，提取段落、表格、标题等内容。
    """

    SUPPORTED_EXTENSIONS = [".docx"]

    def parse(self, file_path: Path) -> ParsedDocument:
        """解析Word文档

        Args:
            file_path: Word文件路径

        Returns:
            解析后的文档对象
        """
        if not self.validate_file(file_path):
            return self._create_error_document(file_path, "文件验证失败")

        try:
            # 提取基础元数据
            metadata = self._extract_metadata(file_path)

            # 解析Word内容
            doc = Document(file_path)

            # 提取元数据
            core_props = doc.core_properties
            metadata["author"] = core_props.author or ""
            metadata["title"] = core_props.title or ""

            # 提取内容
            content_parts = []
            sections = []
            current_section = []

            for element in doc.element.body:
                # 处理段落
                if element.tag.endswith("}p"):
                    paragraph_text = self._extract_paragraph_text(element, doc)
                    if paragraph_text.strip():
                        current_section.append(paragraph_text)

                        # 检查是否是标题
                        style_name = self._get_paragraph_style(element, doc)
                        if style_name and style_name.startswith("Heading"):
                            # 保存之前的部分
                            if current_section:
                                sections.append("\n".join(current_section))
                                current_section = []
                            content_parts.append(f"[{style_name}] {paragraph_text}")

                # 处理表格
                elif element.tag.endswith("}tbl"):
                    table_text = self._extract_table_text(element, doc)
                    if table_text.strip():
                        current_section.append(table_text)

            # 保存最后一部分
            if current_section:
                sections.append("\n".join(current_section))

            # 构建完整内容
            full_content = "\n\n".join(content_parts + sections)

            # 创建文档对象
            parsed_doc = ParsedDocument(
                doc_id=metadata["doc_id"],
                doc_name=metadata["doc_name"],
                doc_type="docx",
                doc_path=metadata["doc_path"],
                content=full_content,
                pages=sections,
                author=metadata.get("author", ""),
                title=metadata.get("title", metadata["doc_name"]),
                created_at=metadata.get("created_at"),
                modified_at=metadata.get("modified_at"),
                page_count=len(sections),
                parse_success=True,
            )

            logger.info(f"Word解析成功: {file_path.name}, 共{len(sections)}个章节")
            return parsed_doc

        except Exception as e:
            logger.error(f"Word解析失败: {file_path.name}, 错误: {e}")
            return self._create_error_document(file_path, str(e))

    def _extract_paragraph_text(self, element, doc: DocumentType) -> str:
        """提取段落文本

        Args:
            element: XML元素
            doc: 文档对象

        Returns:
            段落文本
        """
        from docx.text.paragraph import Paragraph

        paragraph = Paragraph(element, doc)
        return paragraph.text.strip()

    def _get_paragraph_style(self, element, doc: DocumentType) -> str:
        """获取段落样式名称

        Args:
            element: XML元素
            doc: 文档对象

        Returns:
            样式名称
        """
        from docx.text.paragraph import Paragraph

        paragraph = Paragraph(element, doc)
        if paragraph.style:
            return paragraph.style.name
        return ""

    def _extract_table_text(self, element, doc: DocumentType) -> str:
        """提取表格文本

        Args:
            element: XML元素
            doc: 文档对象

        Returns:
            表格文本
        """
        from docx.table import Table

        table = Table(element, doc)
        rows = []

        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                rows.append(" | ".join(cells))

        return "\n".join(rows)
