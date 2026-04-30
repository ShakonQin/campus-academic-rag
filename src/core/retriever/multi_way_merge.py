"""多路归并融合检索"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.utils.logger import logger


@dataclass
class RetrievalResult:
    """检索结果"""

    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    scores: Dict[str, float]  # 各通道分数
    final_score: float = 0.0  # 最终融合分数
    retrieval_channels: List[str] = None  # 来源通道

    def __post_init__(self):
        if self.retrieval_channels is None:
            self.retrieval_channels = []


class MultiWayMerger:
    """多路归并融合器

    对多通道召回结果进行去重、加权打分、重排序。
    """

    def __init__(
        self,
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        """初始化多路归并器

        Args:
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        """
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight

    def merge(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """合并多路检索结果

        Args:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            top_k: 返回结果数量

        Returns:
            合并后的结果列表
        """
        # 收集所有结果
        result_map: Dict[str, RetrievalResult] = {}

        # 处理向量检索结果
        for result in vector_results:
            chunk_id = result["chunk_id"]
            similarity = result.get("similarity", 0.0)

            if chunk_id in result_map:
                result_map[chunk_id].scores["vector"] = similarity
                result_map[chunk_id].retrieval_channels.append("vector")
            else:
                result_map[chunk_id] = RetrievalResult(
                    chunk_id=chunk_id,
                    content=result["content"],
                    metadata=result.get("metadata", {}),
                    scores={"vector": similarity},
                    retrieval_channels=["vector"],
                )

        # 处理关键词检索结果
        for result in keyword_results:
            chunk_id = result["chunk_id"]
            bm25_score = result.get("bm25_score", 0.0)

            # 归一化BM25分数到0-1范围
            normalized_score = self._normalize_bm25_score(bm25_score)

            if chunk_id in result_map:
                result_map[chunk_id].scores["keyword"] = normalized_score
                result_map[chunk_id].retrieval_channels.append("keyword")
            else:
                result_map[chunk_id] = RetrievalResult(
                    chunk_id=chunk_id,
                    content=result["content"],
                    metadata=result.get("metadata", {}),
                    scores={"keyword": normalized_score},
                    retrieval_channels=["keyword"],
                )

        # 计算融合分数
        for result in result_map.values():
            result.final_score = self._calculate_final_score(result)

        # 排序并返回Top-K
        sorted_results = sorted(
            result_map.values(),
            key=lambda x: x.final_score,
            reverse=True,
        )

        merged_results = sorted_results[:top_k]
        logger.debug(
            f"多路归并完成: 向量{len(vector_results)} + 关键词{len(keyword_results)} -> 合并后{len(result_map)} -> Top-K {len(merged_results)}"
        )

        return merged_results

    def _calculate_final_score(self, result: RetrievalResult) -> float:
        """计算融合分数

        Args:
            result: 检索结果

        Returns:
            融合分数
        """
        vector_score = result.scores.get("vector", 0.0)
        keyword_score = result.scores.get("keyword", 0.0)

        # 加权融合
        final_score = (
            self.vector_weight * vector_score + self.keyword_weight * keyword_score
        )

        # 多通道召回奖励（同时出现在多个通道的结果加分）
        if len(result.retrieval_channels) > 1:
            final_score *= 1.1  # 10%奖励

        return final_score

    def _normalize_bm25_score(self, score: float) -> float:
        """归一化BM25分数

        Args:
            score: 原始BM25分数

        Returns:
            归一化后的分数（0-1）
        """
        # 使用sigmoid函数归一化
        import math
        return 1 / (1 + math.exp(-score))

    def set_weights(self, vector_weight: float, keyword_weight: float) -> None:
        """设置检索权重

        Args:
            vector_weight: 向量检索权重
            keyword_weight: 关键词检索权重
        """
        self.vector_weight = vector_weight
        self.keyword_weight = keyword_weight
        logger.info(f"检索权重已更新: 向量={vector_weight}, 关键词={keyword_weight}")
