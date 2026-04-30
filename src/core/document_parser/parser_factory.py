"""文档解析器工厂"""

from pathlib import Path
from typing import Dict, Optional, Type

from src.core.document_parser.base_parser import BaseParser, ParsedDocument
from src.core.document_parser.pdf_parser import PDFParser
from src.core.document_parser.ppt_parser import PPTParser
from src.core.document_parser.docx_parser import DOCXParser
from src.core.document_parser.text_parser import TextParser, MarkdownParser
from src.utils.logger import logger


class ParserFactory:
    """文档解析器工厂

    根据文件扩展名自动选择合适的解析器。
    """

    # 解析器注册表
    _parsers: Dict[str, Type[BaseParser]] = {}

    @classmethod
    def _register_default_parsers(cls) -> None:
        """注册默认解析器"""
        if cls._parsers:
            return

        # 注册PDF解析器
        pdf_parser = PDFParser()
        for ext in pdf_parser.SUPPORTED_EXTENSIONS:
            cls._parsers[ext] = PDFParser

        # 注册PPT解析器
        ppt_parser = PPTParser()
        for ext in ppt_parser.SUPPORTED_EXTENSIONS:
            cls._parsers[ext] = PPTParser

        # 注册Word解析器
        docx_parser = DOCXParser()
        for ext in docx_parser.SUPPORTED_EXTENSIONS:
            cls._parsers[ext] = DOCXParser

        # 注册Markdown解析器
        md_parser = MarkdownParser()
        for ext in md_parser.SUPPORTED_EXTENSIONS:
            cls._parsers[ext] = MarkdownParser

        # 注册纯文本解析器
        txt_parser = TextParser()
        for ext in txt_parser.SUPPORTED_EXTENSIONS:
            cls._parsers[ext] = TextParser

    @classmethod
    def get_parser(cls, file_path: Path) -> Optional[BaseParser]:
        """获取解析器实例

        Args:
            file_path: 文件路径

        Returns:
            解析器实例，如果不支持则返回None
        """
        cls._register_default_parsers()

        extension = file_path.suffix.lower()
        parser_class = cls._parsers.get(extension)

        if parser_class:
            return parser_class()

        return None

    @classmethod
    def parse(cls, file_path: Path) -> ParsedDocument:
        """解析文档

        Args:
            file_path: 文件路径

        Returns:
            解析后的文档对象
        """
        parser = cls.get_parser(file_path)

        if parser is None:
            logger.error(f"不支持的文件格式: {file_path.suffix}")
            return ParsedDocument(
                doc_id=str(file_path.stem),
                doc_name=file_path.name,
                doc_type=file_path.suffix.lower().lstrip("."),
                doc_path=str(file_path),
                parse_success=False,
                error_message=f"不支持的文件格式: {file_path.suffix}",
            )

        return parser.parse(file_path)

    @classmethod
    def register_parser(
        cls, extensions: list, parser_class: Type[BaseParser]
    ) -> None:
        """注册自定义解析器

        Args:
            extensions: 支持的文件扩展名列表
            parser_class: 解析器类
        """
        for ext in extensions:
            cls._parsers[ext.lower()] = parser_class
        logger.info(f"已注册解析器: {extensions} -> {parser_class.__name__}")

    @classmethod
    def get_supported_extensions(cls) -> list:
        """获取所有支持的文件扩展名

        Returns:
            支持的扩展名列表
        """
        cls._register_default_parsers()
        return list(cls._parsers.keys())
