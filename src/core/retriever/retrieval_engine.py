"""检索引擎 - 整合多路检索"""

from typing import List, Dict, Any, Optional

from src.core.retriever.vector_retriever import VectorRetriever
from src.core.retriever.keyword_retriever import KeywordRetriever
from src.core.retriever.multi_way_merge import MultiWayMerger, RetrievalResult
from src.core.retriever.reranker import RerankerFactory, BaseReranker
from src.config.settings import settings
from src.utils.logger import logger


class RetrievalEngine:
    """检索引擎

    整合向量检索、关键词检索、多路归并和重排序。
    """

    def __init__(
        self,
        vector_retriever: Optional[VectorRetriever] = None,
        keyword_retriever: Optional[KeywordRetriever] = None,
        merger: Optional[MultiWayMerger] = None,
        reranker: Optional[BaseReranker] = None,
    ):
        """初始化检索引擎

        Args:
            vector_retriever: 向量检索器
            keyword_retriever: 关键词检索器
            merger: 多路归并器
            reranker: 重排序器
        """
        self.vector_retriever = vector_retriever or VectorRetriever()
        self.keyword_retriever = keyword_retriever or KeywordRetriever()
        self.merger = merger or MultiWayMerger(
            vector_weight=settings.retrieval.vector_weight,
            keyword_weight=settings.retrieval.bm25_weight,
        )
        self.reranker = reranker or RerankerFactory.get_reranker("simple")

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        use_vector: bool = True,
        use_keyword: bool = True,
        use_reranker: bool = True,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """执行检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            use_vector: 是否使用向量检索
            use_keyword: 是否使用关键词检索
            use_reranker: 是否使用重排序
            filter_metadata: 元数据过滤条件

        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = settings.retrieval.retrieval_top_k

        # 多路召回
        vector_results = []
        keyword_results = []

        if use_vector:
            vector_results = self.vector_retriever.retrieve(
                query=query,
                top_k=top_k * 2,  # 召回更多结果用于归并
                filter_metadata=filter_metadata,
            )

        if use_keyword:
            keyword_results = self.keyword_retriever.retrieve(
                query=query,
                top_k=top_k * 2,
            )

        # 多路归并
        merged_results = self.merger.merge(
            vector_results=vector_results,
            keyword_results=keyword_results,
            top_k=top_k * 2,
        )

        # 重排序
        if use_reranker and merged_results:
            final_results = self.reranker.rerank(
                query=query,
                results=merged_results,
                top_k=top_k,
            )
        else:
            final_results = merged_results[:top_k]

        logger.info(
            f"检索完成: query='{query[:30]}...', "
            f"向量={len(vector_results)}, 关键词={len(keyword_results)}, "
            f"归并后={len(merged_results)}, 最终={len(final_results)}"
        )

        return final_results

    def build_indexes(self, chunks) -> None:
        """构建索引

        Args:
            chunks: 分片列表
        """
        # 构建向量索引
        self.vector_retriever.index_builder.add_chunks(chunks)

        # 构建关键词索引
        self.keyword_retriever.build_index(chunks)

        logger.info(f"索引构建完成: {len(chunks)}个分片")

    def set_weights(self, vector_weight: float, keyword_weight: float) -> None:
        """设置检索权重

        Args:
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        """
        self.merger.set_weights(vector_weight, keyword_weight)
