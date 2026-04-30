"""向量语义检索器"""

from typing import List, Dict, Any, Optional

from src.core.embedding.index_builder import VectorIndexBuilder
from src.core.embedding.embedding_engine import EmbeddingFactory, BaseEmbedding
from src.utils.logger import logger


class VectorRetriever:
    """向量语义检索器

    基于嵌入模型的语义匹配召回。
    """

    def __init__(
        self,
        index_builder: Optional[VectorIndexBuilder] = None,
        embedding: Optional[BaseEmbedding] = None,
    ):
        """初始化向量检索器

        Args:
            index_builder: 向量索引构建器
            embedding: 嵌入模型
        """
        self.embedding = embedding or EmbeddingFactory.get_embedding()
        self.index_builder = index_builder or VectorIndexBuilder(embedding=self.embedding)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        collection_name: Optional[str] = None,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """向量语义检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            collection_name: 集合名称
            filter_metadata: 元数据过滤条件

        Returns:
            检索结果列表
        """
        try:
            results = self.index_builder.search(
                query=query,
                top_k=top_k,
                collection_name=collection_name,
                filter_metadata=filter_metadata,
            )

            # 添加检索通道标识
            for result in results:
                result["retrieval_channel"] = "vector"

            logger.debug(f"向量检索返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            return []
