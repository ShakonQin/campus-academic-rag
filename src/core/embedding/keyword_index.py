"""关键词索引模块 - BM25"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import pickle

from src.core.chunker.base_chunker import Chunk
from src.utils.logger import logger


class BM25Index:
    """BM25关键词索引

    基于BM25算法的关键词检索，支持中文分词。
    """

    def __init__(self):
        """初始化BM25索引"""
        self._bm25 = None
        self._corpus = []
        self._chunk_map: Dict[str, Chunk] = {}
        self._tokenized_corpus = []

    def _tokenize(self, text: str) -> List[str]:
        """中文分词

        Args:
            text: 文本内容

        Returns:
            分词结果
        """
        try:
            import jieba
            # 精确模式分词
            tokens = list(jieba.cut(text))
            # 过滤停用词和空白
            tokens = [t.strip() for t in tokens if t.strip() and len(t.strip()) > 1]
            return tokens
        except ImportError:
            logger.warning("jieba未安装，使用简单分词")
            # 简单分词（按字符）
            return list(text)

    def build_index(self, chunks: List[Chunk]) -> None:
        """构建BM25索引

        Args:
            chunks: 分片列表
        """
        if not chunks:
            logger.warning("没有分片需要索引")
            return

        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.error("rank-bm25未安装，请运行: pip install rank-bm25")
            raise

        # 保存分片映射
        self._chunk_map = {chunk.chunk_id: chunk for chunk in chunks}

        # 分词
        self._corpus = [chunk.content for chunk in chunks]
        self._tokenized_corpus = [self._tokenize(text) for text in self._corpus]

        # 构建BM25索引
        self._bm25 = BM25Okapi(self._tokenized_corpus)

        logger.info(f"BM25索引构建完成: {len(chunks)}个分片")

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter_fn=None,
    ) -> List[Dict[str, Any]]:
        """BM25关键词检索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_fn: 过滤函数，接收Chunk对象，返回bool

        Returns:
            检索结果列表
        """
        if self._bm25 is None:
            logger.error("BM25索引未构建")
            return []

        # 查询分词
        query_tokens = self._tokenize(query)

        # BM25打分
        scores = self._bm25.get_scores(query_tokens)

        # 获取所有结果并排序
        results = []
        for i, score in enumerate(scores):
            chunk_id = list(self._chunk_map.keys())[i]
            chunk = self._chunk_map[chunk_id]

            # 应用过滤
            if filter_fn and not filter_fn(chunk):
                continue

            results.append({
                "chunk_id": chunk_id,
                "content": chunk.content,
                "metadata": chunk.to_dict()["metadata"],
                "bm25_score": float(score),
            })

        # 按分数排序
        results.sort(key=lambda x: x["bm25_score"], reverse=True)

        return results[:top_k]

    def save(self, path: str) -> None:
        """保存索引到文件

        Args:
            path: 保存路径
        """
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "corpus": self._corpus,
            "tokenized_corpus": self._tokenized_corpus,
            "chunk_map": {k: v.to_dict() for k, v in self._chunk_map.items()},
        }

        with open(save_path, "wb") as f:
            pickle.dump(data, f)

        logger.info(f"BM25索引已保存: {path}")

    def load(self, path: str) -> None:
        """从文件加载索引

        Args:
            path: 索引文件路径
        """
        try:
            from rank_bm25 import BM25Okapi
        except ImportError:
            logger.error("rank-bm25未安装")
            raise

        load_path = Path(path)
        if not load_path.exists():
            logger.error(f"索引文件不存在: {path}")
            return

        with open(load_path, "rb") as f:
            data = pickle.load(f)

        self._corpus = data["corpus"]
        self._tokenized_corpus = data["tokenized_corpus"]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

        # 重建chunk映射
        self._chunk_map = {}
        for chunk_id, chunk_data in data["chunk_map"].items():
            chunk = Chunk(
                chunk_id=chunk_id,
                content=chunk_data["content"],
            )
            self._chunk_map[chunk_id] = chunk

        logger.info(f"BM25索引已加载: {path}, {len(self._chunk_map)}个分片")

    def get_stats(self) -> Dict[str, Any]:
        """获取索引统计信息

        Returns:
            统计信息字典
        """
        return {
            "total_chunks": len(self._chunk_map),
            "index_built": self._bm25 is not None,
        }
