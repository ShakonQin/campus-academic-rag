"""索引构建工具"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import hashlib

from src.core.chunker.base_chunker import Chunk
from src.core.embedding.embedding_engine import EmbeddingFactory, BaseEmbedding
from src.config.settings import settings
from src.utils.logger import logger


class VectorIndexBuilder:
    """向量索引构建器

    负责将文档分片构建为向量索引，支持ChromaDB。
    """

    def __init__(self, embedding: Optional[BaseEmbedding] = None):
        """初始化索引构建器

        Args:
            embedding: 嵌入模型实例
        """
        self.embedding = embedding or EmbeddingFactory.get_embedding()
        self._client = None
        self._collection = None

    def _get_client(self):
        """获取ChromaDB客户端"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings as ChromaSettings

                # 确保目录存在
                db_path = Path(settings.vector_db.vector_db_path)
                db_path.mkdir(parents=True, exist_ok=True)

                self._client = chromadb.PersistentClient(
                    path=str(db_path),
                    settings=ChromaSettings(anonymized_telemetry=False),
                )
                logger.info(f"ChromaDB客户端初始化成功: {db_path}")
            except ImportError:
                logger.error("chromadb未安装，请运行: pip install chromadb")
                raise
        return self._client

    def _get_collection(self, collection_name: Optional[str] = None):
        """获取或创建集合

        Args:
            collection_name: 集合名称

        Returns:
            ChromaDB集合对象
        """
        if self._collection is None:
            client = self._get_client()
            name = collection_name or settings.vector_db.vector_db_collection

            self._collection = client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"},  # 使用余弦相似度
            )
            logger.info(f"集合已就绪: {name}")
        return self._collection

    def add_chunks(
        self,
        chunks: List[Chunk],
        collection_name: Optional[str] = None,
        batch_size: int = 100,
    ) -> int:
        """将分片添加到向量索引

        Args:
            chunks: 分片列表
            collection_name: 集合名称
            batch_size: 批处理大小

        Returns:
            添加的分片数量
        """
        if not chunks:
            logger.warning("没有分片需要添加")
            return 0

        collection = self._get_collection(collection_name)

        # 批量处理
        total_added = 0
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]

            # 准备数据
            ids = [chunk.chunk_id for chunk in batch]
            documents = [chunk.content for chunk in batch]
            metadatas = [self._prepare_metadata(chunk) for chunk in batch]

            # 生成嵌入向量
            embeddings = self.embedding.encode(documents)
            # 确保是list格式
            if hasattr(embeddings, 'tolist'):
                embeddings = embeddings.tolist()

            # 添加到集合（upsert: 已存在则更新，不存在则插入）
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            total_added += len(batch)
            logger.debug(f"已添加 {total_added}/{len(chunks)} 个分片")

        logger.info(f"向量索引构建完成: 添加了 {total_added} 个分片")
        return total_added

    def _prepare_metadata(self, chunk: Chunk) -> Dict[str, Any]:
        """准备元数据（ChromaDB要求值为基本类型）

        Args:
            chunk: 分片对象

        Returns:
            元数据字典
        """
        metadata = chunk.metadata
        return {
            "doc_id": metadata.doc_id,
            "doc_name": metadata.doc_name,
            "doc_type": metadata.doc_type,
            "doc_path": metadata.doc_path,
            "page_number": metadata.page_number,
            "chunk_index": metadata.chunk_index,
            "chapter": metadata.chapter,
            "section": metadata.section,
            "title": metadata.title,
            "content_type": metadata.content_type,
            "has_formula": metadata.has_formula,
            "has_table": metadata.has_table,
            "has_figure": metadata.has_figure,
            "author": metadata.author,
            "course_name": metadata.course_name,
            "tags": ",".join(metadata.tags) if metadata.tags else "",
        }

    def search(
        self,
        query: str,
        top_k: int = 10,
        collection_name: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """搜索相似分片

        Args:
            query: 查询文本
            top_k: 返回结果数量
            collection_name: 集合名称
            filter_metadata: 元数据过滤条件

        Returns:
            搜索结果列表
        """
        collection = self._get_collection(collection_name)

        # 生成查询向量
        query_embedding = self.embedding.encode(query)
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()

        # 构建过滤条件
        where = None
        if filter_metadata:
            where = self._build_where_filter(filter_metadata)

        # 执行搜索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        # 格式化结果
        formatted_results = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                result = {
                    "chunk_id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                    "similarity": 1 - results["distances"][0][i],  # 余弦相似度
                }
                formatted_results.append(result)

        return formatted_results

    def _build_where_filter(self, filter_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """构建ChromaDB的where过滤条件

        Args:
            filter_metadata: 过滤条件字典

        Returns:
            ChromaDB where条件
        """
        conditions = []
        for key, value in filter_metadata.items():
            if isinstance(value, str):
                conditions.append({key: {"$eq": value}})
            elif isinstance(value, list):
                conditions.append({key: {"$in": value}})
            elif isinstance(value, bool):
                conditions.append({key: {"$eq": value}})

        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"$and": conditions}
        return {}

    def delete_collection(self, collection_name: Optional[str] = None) -> None:
        """删除集合

        Args:
            collection_name: 集合名称
        """
        client = self._get_client()
        name = collection_name or settings.vector_db.vector_db_collection
        try:
            client.delete_collection(name)
            logger.info(f"集合已删除: {name}")
        except ValueError:
            logger.warning(f"集合不存在: {name}")

    def get_collection_stats(self, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """获取集合统计信息

        Args:
            collection_name: 集合名称

        Returns:
            统计信息字典
        """
        collection = self._get_collection(collection_name)
        return {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata,
        }
