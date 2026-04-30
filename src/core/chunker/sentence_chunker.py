"""按句分片器 - 实现滑动窗口分片策略"""

import re
from typing import List, Optional

from src.core.chunker.base_chunker import BaseChunker, Chunk, ChunkMetadata
from src.utils.logger import logger


class SentenceChunker(BaseChunker):
    """按句分片器

    实现按句分片+滑动窗口的分片策略：
    1. 以完整句子为最小分片单元
    2. 默认3句为一个分片单元
    3. 相邻分片重叠1句
    4. 对标题、公式、图表做特殊处理
    """

    def __init__(
        self,
        sentences_per_chunk: int = 3,
        overlap_sentences: int = 1,
        max_chunk_length: int = 512,
    ):
        """初始化分片器

        Args:
            sentences_per_chunk: 每个分片的句子数
            overlap_sentences: 重叠句子数
            max_chunk_length: 分片最大长度
        """
        self.sentences_per_chunk = sentences_per_chunk
        self.overlap_sentences = overlap_sentences
        self.max_chunk_length = max_chunk_length

        # 中英文句子结束标记
        self.sentence_endings = re.compile(r"[。！？.!?；;]")

    def chunk(
        self, content: str, metadata: Optional[ChunkMetadata] = None
    ) -> List[Chunk]:
        """对内容进行分片

        Args:
            content: 文本内容
            metadata: 基础元数据

        Returns:
            分片列表
        """
        if not content or not content.strip():
            return []

        # 分句
        sentences = self._split_sentences(content)
        if not sentences:
            return []

        # 处理特殊情况：句子数少于每个分片的句子数
        if len(sentences) <= self.sentences_per_chunk:
            chunk_content = " ".join(sentences)
            if len(chunk_content) > self.max_chunk_length:
                chunk_content = chunk_content[:self.max_chunk_length]
            doc_id = metadata.doc_id if metadata else "unknown"
            return [self._create_chunk(chunk_content, doc_id, 0, metadata)]

        # 滑动窗口分片
        chunks = []
        chunk_index = 0
        start_idx = 0

        while start_idx < len(sentences):
            # 计算当前分片的结束位置
            end_idx = min(start_idx + self.sentences_per_chunk, len(sentences))

            # 提取分片内容
            chunk_sentences = sentences[start_idx:end_idx]
            chunk_content = " ".join(chunk_sentences)

            # 检查长度限制
            if len(chunk_content) > self.max_chunk_length:
                # 尝试减少句子数
                while len(chunk_content) > self.max_chunk_length and len(chunk_sentences) > 1:
                    chunk_sentences.pop()
                    end_idx -= 1
                    chunk_content = " ".join(chunk_sentences)

            # 创建分片
            doc_id = metadata.doc_id if metadata else "unknown"
            chunk = self._create_chunk(
                content=chunk_content,
                doc_id=doc_id,
                chunk_index=chunk_index,
                base_metadata=metadata,
                start_char=self._get_char_position(sentences, start_idx),
                end_char=self._get_char_position(sentences, end_idx),
            )
            chunks.append(chunk)
            chunk_index += 1

            # 移动到下一个位置（考虑重叠）
            start_idx += self.sentences_per_chunk - self.overlap_sentences

            # 防止无限循环
            if start_idx >= len(sentences):
                break

            # 如果剩余句子不足一个完整分片，将剩余句子加入最后一个分片
            if len(sentences) - start_idx < self.sentences_per_chunk:
                remaining = " ".join(sentences[start_idx:])
                if remaining.strip():
                    # 更新最后一个分片，加入剩余内容
                    chunks[-1].content = chunks[-1].content + " " + remaining
                break

        logger.debug(f"分片完成: {len(sentences)}句 -> {len(chunks)}个分片")
        return chunks

    def _split_sentences(self, text: str) -> List[str]:
        """分句

        Args:
            text: 文本内容

        Returns:
            句子列表
        """
        # 处理特殊情况
        if not text:
            return []

        # 分句策略：
        # 1. 按句号、感叹号、问号分句
        # 2. 保留分隔符
        # 3. 处理标题行（没有句号结尾的行）

        sentences = []
        current_sentence = ""

        for char in text:
            current_sentence += char

            # 检查是否是句子结束
            if self.sentence_endings.match(char):
                sentence = current_sentence.strip()
                if sentence:
                    sentences.append(sentence)
                current_sentence = ""

        # 处理最后一个没有结束符的句子
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        # 进一步处理：合并过短的句子
        merged_sentences = []
        for sentence in sentences:
            # 如果句子过短且前一个句子也短，合并它们
            if len(sentence) < 10 and merged_sentences and len(merged_sentences[-1]) < 50:
                merged_sentences[-1] += " " + sentence
            else:
                merged_sentences.append(sentence)

        return merged_sentences

    def _get_char_position(self, sentences: List[str], index: int) -> int:
        """获取句子在原文中的字符位置

        Args:
            sentences: 句子列表
            index: 句子索引

        Returns:
            字符位置
        """
        if index <= 0:
            return 0
        return sum(len(s) + 1 for s in sentences[:index])  # +1 for space


class DocumentChunker:
    """文档分片器

    处理解析后的文档，按页/章节分片。
    """

    def __init__(
        self,
        sentences_per_chunk: int = 3,
        overlap_sentences: int = 1,
        max_chunk_length: int = 512,
    ):
        """初始化文档分片器

        Args:
            sentences_per_chunk: 每个分片的句子数
            overlap_sentences: 重叠句子数
            max_chunk_length: 分片最大长度
        """
        self.sentence_chunker = SentenceChunker(
            sentences_per_chunk=sentences_per_chunk,
            overlap_sentences=overlap_sentences,
            max_chunk_length=max_chunk_length,
        )

    def chunk_document(
        self,
        content: str,
        pages: List[str],
        doc_id: str,
        doc_name: str,
        doc_type: str,
        doc_path: str = "",
        author: str = "",
        course_name: str = "",
        chapter: str = "",
        title: str = "",
        **kwargs,
    ) -> List[Chunk]:
        """对文档进行分片

        Args:
            content: 文档完整内容
            pages: 按页/章节分割的内容
            doc_id: 文档ID
            doc_name: 文档名称
            doc_type: 文档类型
            doc_path: 文档路径
            author: 作者
            course_name: 课程名称
            chapter: 章节
            title: 标题
            **kwargs: 其他元数据

        Returns:
            分片列表
        """
        all_chunks = []
        chunk_index = 0

        # 如果没有页面分割，对整个内容分片
        if not pages:
            base_metadata = ChunkMetadata(
                doc_id=doc_id,
                doc_name=doc_name,
                doc_type=doc_type,
                doc_path=doc_path,
                author=author,
                course_name=course_name,
                chapter=chapter,
                title=title,
                tags=kwargs.get("tags", []),
            )
            chunks = self.sentence_chunker.chunk(content, base_metadata)
            for chunk in chunks:
                chunk.metadata.chunk_index = chunk_index
                chunk_index += 1
            all_chunks.extend(chunks)
        else:
            # 按页/章节分片
            for page_num, page_content in enumerate(pages, 1):
                if not page_content.strip():
                    continue

                # 创建页面元数据
                base_metadata = ChunkMetadata(
                    doc_id=doc_id,
                    doc_name=doc_name,
                    doc_type=doc_type,
                    doc_path=doc_path,
                    page_number=page_num,
                    author=author,
                    course_name=course_name,
                    chapter=chapter,
                    title=title,
                    tags=kwargs.get("tags", []),
                )

                # 对页面内容分片
                chunks = self.sentence_chunker.chunk(page_content, base_metadata)
                for chunk in chunks:
                    chunk.metadata.chunk_index = chunk_index
                    chunk.metadata.page_number = page_num
                    chunk_index += 1

                all_chunks.extend(chunks)

        logger.info(
            f"文档分片完成: {doc_name}, 共{len(all_chunks)}个分片"
        )
        return all_chunks
