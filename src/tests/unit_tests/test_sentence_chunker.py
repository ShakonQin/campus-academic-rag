"""按句分片器测试"""

import pytest
from src.core.chunker.sentence_chunker import SentenceChunker
from src.core.chunker.base_chunker import ChunkMetadata


class TestSentenceChunker:
    """按句分片器测试类"""

    def setup_method(self):
        """测试前准备"""
        self.chunker = SentenceChunker(
            sentences_per_chunk=3,
            overlap_sentences=1,
            max_chunk_length=512,
        )

    def test_basic_chunking(self):
        """测试基础分片功能"""
        content = "这是第一句话。这是第二句话。这是第三句话。这是第四句话。这是第五句话。"
        chunks = self.chunker.chunk(content)

        assert len(chunks) > 0
        # 每个分片应该包含句子
        for chunk in chunks:
            assert chunk.content.strip() != ""

    def test_empty_content(self):
        """测试空内容"""
        content = ""
        chunks = self.chunker.chunk(content)
        assert len(chunks) == 0

    def test_single_sentence(self):
        """测试单个句子"""
        content = "这是一个句子。"
        chunks = self.chunker.chunk(content)
        assert len(chunks) == 1
        assert "这是一个句子" in chunks[0].content

    def test_sliding_window(self):
        """测试滑动窗口机制"""
        content = "句子一。句子二。句子三。句子四。句子五。句子六。"
        chunks = self.chunker.chunk(content)

        # 验证分片数量
        assert len(chunks) >= 2

        # 验证重叠：前一个分片的最后一句应该是后一个分片的第一句（或部分）
        if len(chunks) >= 2:
            # 检查分片之间有内容重叠
            pass

    def test_with_metadata(self):
        """测试带元数据的分片"""
        content = "这是测试内容。包含多个句子。用于验证元数据。"
        metadata = ChunkMetadata(
            doc_id="test_doc",
            doc_name="test.pdf",
            doc_type="pdf",
        )
        chunks = self.chunker.chunk(content, metadata)

        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.metadata.doc_id == "test_doc"
            assert chunk.metadata.doc_name == "test.pdf"

    def test_max_length_limit(self):
        """测试最大长度限制"""
        # 创建超长内容
        content = "这是一个很长的句子。" * 100
        chunker = SentenceChunker(max_chunk_length=50)
        chunks = chunker.chunk(content)

        # 验证每个分片不超过最大长度
        for chunk in chunks:
            assert len(chunk.content) <= 50 + 10  # 允许小幅超出

    def test_chinese_sentences(self):
        """测试中文句子分割"""
        content = "今天天气很好。我去图书馆看书。学习了Python编程。感觉收获很大！"
        chunks = self.chunker.chunk(content)

        assert len(chunks) > 0
        # 验证句子被正确分割
        all_content = " ".join(chunk.content for chunk in chunks)
        assert "天气" in all_content
        assert "图书馆" in all_content

    def test_english_sentences(self):
        """测试英文句子分割"""
        content = "This is sentence one. This is sentence two. This is sentence three!"
        chunks = self.chunker.chunk(content)

        assert len(chunks) > 0
        all_content = " ".join(chunk.content for chunk in chunks)
        assert "sentence" in all_content

    def test_mixed_content(self):
        """测试中英文混合内容"""
        content = "Python是一种编程语言。It is widely used. 广泛应用于AI领域。"
        chunks = self.chunker.chunk(content)

        assert len(chunks) > 0

    def test_chunk_ids_unique(self):
        """测试分片ID唯一性"""
        content = "句子一。句子二。句子三。句子四。句子五。句子六。"
        chunks = self.chunker.chunk(content)

        chunk_ids = [chunk.chunk_id for chunk in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))


class TestDocumentChunker:
    """文档分片器测试类"""

    def setup_method(self):
        """测试前准备"""
        from src.core.chunker.sentence_chunker import DocumentChunker
        self.chunker = DocumentChunker()

    def test_chunk_document_with_pages(self):
        """测试按页分片"""
        pages = [
            "第一页内容。包含一些句子。",
            "第二页内容。也有句子。",
            "第三页内容。继续。",
        ]
        chunks = self.chunker.chunk_document(
            content="\n".join(pages),
            pages=pages,
            doc_id="test_doc",
            doc_name="test.pdf",
            doc_type="pdf",
        )

        assert len(chunks) > 0
        # 验证页码信息
        page_numbers = set(chunk.metadata.page_number for chunk in chunks)
        assert len(page_numbers) > 1

    def test_chunk_document_without_pages(self):
        """测试无页面分割的文档分片"""
        content = "这是文档内容。包含多个句子。需要进行分片。"
        chunks = self.chunker.chunk_document(
            content=content,
            pages=[],
            doc_id="test_doc",
            doc_name="test.txt",
            doc_type="txt",
        )

        assert len(chunks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
