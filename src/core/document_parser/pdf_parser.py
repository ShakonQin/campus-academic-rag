"""PDF文档解析器"""

from pathlib import Path
from typing import List

import pdfplumber

from src.core.document_parser.base_parser import BaseParser, ParsedDocument
from src.utils.logger import logger


class PDFParser(BaseParser):
    """PDF文档解析器

    支持解析标准PDF文档，提取文本内容、元数据，按页分割。
    """

    SUPPORTED_EXTENSIONS = [".pdf"]

    def parse(self, file_path: Path) -> ParsedDocument:
        """解析PDF文档

        Args:
            file_path: PDF文件路径

        Returns:
            解析后的文档对象
        """
        if not self.validate_file(file_path):
            return self._create_error_document(file_path, "文件验证失败")

        try:
            # 提取基础元数据
            metadata = self._extract_metadata(file_path)

            # 解析PDF内容
            pages = []
            full_content_parts = []
            page_count = 0

            with pdfplumber.open(file_path) as pdf:
                # 提取PDF元数据
                pdf_metadata = pdf.metadata or {}
                metadata["author"] = pdf_metadata.get("Author", "")
                metadata["title"] = pdf_metadata.get("Title", "")

                # 逐页解析
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            # 清理文本
                            text = self._clean_text(text)
                            if text.strip():
                                pages.append(text)
                                full_content_parts.append(f"[第{page_num}页]\n{text}")
                                page_count += 1
                    except Exception as e:
                        logger.warning(f"解析PDF第{page_num}页失败: {e}")
                        continue

            # 构建完整内容
            full_content = "\n\n".join(full_content_parts)

            # 创建文档对象
            doc = ParsedDocument(
                doc_id=metadata["doc_id"],
                doc_name=metadata["doc_name"],
                doc_type="pdf",
                doc_path=metadata["doc_path"],
                content=full_content,
                pages=pages,
                author=metadata.get("author", ""),
                title=metadata.get("title", metadata["doc_name"]),
                created_at=metadata.get("created_at"),
                modified_at=metadata.get("modified_at"),
                page_count=page_count,
                parse_success=True,
            )

            logger.info(f"PDF解析成功: {file_path.name}, 共{page_count}页")
            return doc

        except Exception as e:
            logger.error(f"PDF解析失败: {file_path.name}, 错误: {e}")
            return self._create_error_document(file_path, str(e))

    def _clean_text(self, text: str) -> str:
        """清理PDF提取的文本

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text:
            return ""

        # 移除多余的空白字符
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)
