"""文档解析模块"""

from src.core.document_parser.base_parser import BaseParser, ParsedDocument
from src.core.document_parser.pdf_parser import PDFParser
from src.core.document_parser.ppt_parser import PPTParser
from src.core.document_parser.docx_parser import DOCXParser
from src.core.document_parser.text_parser import TextParser, MarkdownParser
from src.core.document_parser.parser_factory import ParserFactory

__all__ = [
    "BaseParser",
    "ParsedDocument",
    "PDFParser",
    "PPTParser",
    "DOCXParser",
    "TextParser",
    "MarkdownParser",
    "ParserFactory",
]
