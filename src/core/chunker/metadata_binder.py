"""元数据绑定工具"""

from typing import List, Optional, Dict, Any

from src.core.chunker.base_chunker import Chunk, ChunkMetadata
from src.utils.logger import logger


class MetadataBinder:
    """元数据绑定器

    为分片绑定额外的元数据信息，包括：
    - 文档级元数据（课程名称、作者等）
    - 内容级元数据（章节、标题等）
    - 自定义标签
    """

    def bind_document_metadata(
        self,
        chunks: List[Chunk],
        metadata: Dict[str, Any],
    ) -> List[Chunk]:
        """绑定文档级元数据

        Args:
            chunks: 分片列表
            metadata: 元数据字典

        Returns:
            绑定元数据后的分片列表
        """
        for chunk in chunks:
            # 绑定文档元数据
            if "doc_id" in metadata:
                chunk.metadata.doc_id = metadata["doc_id"]
            if "doc_name" in metadata:
                chunk.metadata.doc_name = metadata["doc_name"]
            if "doc_type" in metadata:
                chunk.metadata.doc_type = metadata["doc_type"]
            if "doc_path" in metadata:
                chunk.metadata.doc_path = metadata["doc_path"]
            if "author" in metadata:
                chunk.metadata.author = metadata["author"]
            if "title" in metadata:
                chunk.metadata.title = metadata["title"]
            if "created_at" in metadata:
                chunk.metadata.created_at = metadata["created_at"]

        return chunks

    def bind_course_metadata(
        self,
        chunks: List[Chunk],
        course_name: str,
        chapter: str = "",
        section: str = "",
        tags: Optional[List[str]] = None,
    ) -> List[Chunk]:
        """绑定课程相关元数据

        Args:
            chunks: 分片列表
            course_name: 课程名称
            chapter: 章节
            section: 小节
            tags: 标签列表

        Returns:
            绑定元数据后的分片列表
        """
        for chunk in chunks:
            chunk.metadata.course_name = course_name
            if chapter:
                chunk.metadata.chapter = chapter
            if section:
                chunk.metadata.section = section
            if tags:
                chunk.metadata.tags.extend(tags)
                # 去重
                chunk.metadata.tags = list(set(chunk.metadata.tags))

        return chunks

    def bind_chapter_info(
        self,
        chunks: List[Chunk],
        chapter_map: Dict[int, Dict[str, str]],
    ) -> List[Chunk]:
        """根据页码绑定章节信息

        Args:
            chunks: 分片列表
            chapter_map: 章节映射，格式: {页码: {"chapter": "章节名", "section": "小节名"}}

        Returns:
            绑定元数据后的分片列表
        """
        for chunk in chunks:
            page_num = chunk.metadata.page_number
            if page_num in chapter_map:
                chapter_info = chapter_map[page_num]
                chunk.metadata.chapter = chapter_info.get("chapter", "")
                chunk.metadata.section = chapter_info.get("section", "")

        return chunks

    def add_tags(
        self,
        chunks: List[Chunk],
        tags: List[str],
    ) -> List[Chunk]:
        """添加标签

        Args:
            chunks: 分片列表
            tags: 标签列表

        Returns:
            添加标签后的分片列表
        """
        for chunk in chunks:
            chunk.metadata.tags.extend(tags)
            # 去重
            chunk.metadata.tags = list(set(chunk.metadata.tags))

        return chunks

    def update_metadata(
        self,
        chunk: Chunk,
        **kwargs,
    ) -> Chunk:
        """更新单个分片的元数据

        Args:
            chunk: 分片对象
            **kwargs: 要更新的元数据字段

        Returns:
            更新后的分片对象
        """
        for key, value in kwargs.items():
            if hasattr(chunk.metadata, key):
                setattr(chunk.metadata, key, value)
            else:
                logger.warning(f"未知的元数据字段: {key}")

        return chunk

    def merge_metadata(
        self,
        base_metadata: Dict[str, Any],
        override_metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """合并元数据

        Args:
            base_metadata: 基础元数据
            override_metadata: 覆盖元数据

        Returns:
            合并后的元数据
        """
        merged = base_metadata.copy()
        merged.update(override_metadata)
        return merged
