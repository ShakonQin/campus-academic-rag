"""重排序引擎"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from src.core.retriever.multi_way_merge import RetrievalResult
from src.utils.logger import logger


class BaseReranker(ABC):
    """重排序基类"""

    @abstractmethod
    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """重排序

        Args:
            query: 查询文本
            results: 检索结果列表
            top_k: 返回结果数量

        Returns:
            重排序后的结果列表
        """
        pass


class SimpleReranker(BaseReranker):
    """简单重排序器

    基于规则的重排序，不依赖额外模型。
    """

    def __init__(
        self,
        length_penalty_weight: float = 0.1,
        diversity_bonus: float = 0.05,
    ):
        """初始化简单重排序器

        Args:
            length_penalty_weight: 长度惩罚权重
            diversity_bonus: 多样性奖励
        """
        self.length_penalty_weight = length_penalty_weight
        self.diversity_bonus = diversity_bonus

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """重排序

        Args:
            query: 查询文本
            results: 检索结果列表
            top_k: 返回结果数量

        Returns:
            重排序后的结果列表
        """
        if not results:
            return []

        # 计算调整后的分数
        for result in results:
            adjusted_score = result.final_score

            # 长度惩罚：过短或过长的内容降低分数
            content_length = len(result.content)
            if content_length < 50:
                adjusted_score *= (1 - self.length_penalty_weight)
            elif content_length > 1000:
                adjusted_score *= (1 - self.length_penalty_weight * 0.5)

            # 查询相关性增强
            query_overlap = self._calculate_query_overlap(query, result.content)
            adjusted_score *= (1 + query_overlap * 0.2)

            result.final_score = adjusted_score

        # 排序
        sorted_results = sorted(
            results,
            key=lambda x: x.final_score,
            reverse=True,
        )

        # 应用多样性惩罚（避免过多相似结果）
        diverse_results = self._apply_diversity(sorted_results)

        logger.debug(f"重排序完成: {len(results)} -> {len(diverse_results[:top_k])}")
        return diverse_results[:top_k]

    def _calculate_query_overlap(self, query: str, content: str) -> float:
        """计算查询与内容的重叠度

        Args:
            query: 查询文本
            content: 内容文本

        Returns:
            重叠度（0-1）
        """
        import jieba

        query_tokens = set(jieba.cut(query))
        content_tokens = set(jieba.cut(content))

        # 移除停用词
        stopwords = {"的", "了", "是", "在", "和", "有", "就", "不", "也", "都", "这", "那"}
        query_tokens -= stopwords
        content_tokens -= stopwords

        if not query_tokens:
            return 0.0

        # 计算重叠比例
        overlap = len(query_tokens & content_tokens)
        return overlap / len(query_tokens)

    def _apply_diversity(
        self, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """应用多样性惩罚

        Args:
            results: 排序后的结果列表

        Returns:
            多样性调整后的结果列表
        """
        if len(results) <= 1:
            return results

        diverse_results = [results[0]]

        for result in results[1:]:
            # 检查与已选结果的相似度
            max_similarity = max(
                self._content_similarity(result.content, selected.content)
                for selected in diverse_results
            )

            # 如果相似度过高，降低分数
            if max_similarity > 0.8:
                result.final_score *= (1 - self.diversity_bonus)

            diverse_results.append(result)

        # 重新排序
        diverse_results.sort(key=lambda x: x.final_score, reverse=True)
        return diverse_results

    def _content_similarity(self, content1: str, content2: str) -> float:
        """计算内容相似度

        Args:
            content1: 内容1
            content2: 内容2

        Returns:
            相似度（0-1）
        """
        import jieba

        tokens1 = set(jieba.cut(content1))
        tokens2 = set(jieba.cut(content2))

        if not tokens1 or not tokens2:
            return 0.0

        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)

        return intersection / union if union > 0 else 0.0


class CrossEncoderReranker(BaseReranker):
    """交叉编码器重排序器

    使用交叉编码器模型进行精排（可选，需要额外模型）。
    """

    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        """初始化交叉编码器重排序器

        Args:
            model_name: 重排序模型名称
        """
        self.model_name = model_name
        self._model = None

    def _load_model(self) -> None:
        """加载重排序模型"""
        if self._model is not None:
            return

        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            logger.info(f"重排序模型已加载: {self.model_name}")
        except ImportError:
            logger.error("sentence-transformers未安装")
            raise
        except Exception as e:
            logger.error(f"重排序模型加载失败: {e}")
            raise

    def rerank(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """使用交叉编码器重排序

        Args:
            query: 查询文本
            results: 检索结果列表
            top_k: 返回结果数量

        Returns:
            重排序后的结果列表
        """
        if not results:
            return []

        self._load_model()

        # 准备输入对
        pairs = [(query, result.content) for result in results]

        # 计算相关性分数
        scores = self._model.predict(pairs)

        # 更新分数
        for result, score in zip(results, scores):
            result.final_score = float(score)

        # 排序
        sorted_results = sorted(
            results,
            key=lambda x: x.final_score,
            reverse=True,
        )

        logger.debug(f"交叉编码器重排序完成: {len(results)} -> {len(sorted_results[:top_k])}")
        return sorted_results[:top_k]


class RerankerFactory:
    """重排序器工厂"""

    @staticmethod
    def get_reranker(
        reranker_type: str = "simple",
        **kwargs,
    ) -> BaseReranker:
        """获取重排序器

        Args:
            reranker_type: 重排序器类型（simple/cross_encoder）
            **kwargs: 额外参数

        Returns:
            重排序器实例
        """
        if reranker_type == "simple":
            return SimpleReranker(**kwargs)
        elif reranker_type == "cross_encoder":
            return CrossEncoderReranker(**kwargs)
        else:
            logger.warning(f"未知的重排序器类型: {reranker_type}，使用简单重排序器")
            return SimpleReranker(**kwargs)
