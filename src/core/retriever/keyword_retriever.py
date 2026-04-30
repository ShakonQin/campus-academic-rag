"""关键词检索器"""

from typing import List, Dict, Any, Optional

from src.core.embedding.keyword_index import BM25Index
from src.utils.logger import logger


class KeywordRetriever:
    """关键词检索器

    基于BM25算法的关键词匹配召回。
    """

    def __init__(self, bm25_index: Optional[BM25Index] = None):
        """初始化关键词检索器

        Args:
            bm25_index: BM25索引实例
        """
        self.bm25_index = bm25_index or BM25Index()

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        filter_fn=None,
    ) -> List[Dict[str, Any]]:
        """关键词检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_fn: 过滤函数

        Returns:
            检索结果列表
        """
        try:
            results = self.bm25_index.search(
                query=query,
                top_k=top_k,
                filter_fn=filter_fn,
            )

            # 添加检索通道标识
            for result in results:
                result["retrieval_channel"] = "keyword"

            logger.debug(f"关键词检索返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"关键词检索失败: {e}")
            return []

    def build_index(self, chunks) -> None:
        """构建BM25索引

        Args:
            chunks: 分片列表
        """
        self.bm25_index.build_index(chunks)
