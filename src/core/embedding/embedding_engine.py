"""嵌入模型引擎"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
import numpy as np

from src.config.settings import settings
from src.utils.logger import logger


class BaseEmbedding(ABC):
    """嵌入模型基类"""

    @abstractmethod
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """将文本转换为向量

        Args:
            texts: 单个文本或文本列表
            **kwargs: 额外参数

        Returns:
            向量或向量矩阵
        """
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """获取向量维度

        Returns:
            向量维度
        """
        pass


class SentenceTransformerEmbedding(BaseEmbedding):
    """基于Sentence Transformers的嵌入模型

    支持加载本地模型或在线模型，推荐使用BGE系列中文模型。
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        model_path: Optional[str] = None,
        device: Optional[str] = None,
    ):
        """初始化嵌入模型

        Args:
            model_name: 模型名称（在线下载）
            model_path: 本地模型路径
            device: 运行设备 (cpu/cuda)
        """
        self._model = None
        self._model_name = model_name or settings.embedding.embedding_model_name
        self._model_path = model_path or settings.embedding.embedding_model_path
        self._device = device or settings.embedding.embedding_device
        self._dimension = settings.embedding.embedding_dimension

    def _load_model(self) -> None:
        """延迟加载模型"""
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer

            # 优先使用本地模型
            if self._model_path:
                import os
                if os.path.exists(self._model_path):
                    logger.info(f"加载本地嵌入模型: {self._model_path}")
                    self._model = SentenceTransformer(
                        self._model_path, device=self._device
                    )
                    return

            # 使用在线模型
            logger.info(f"加载在线嵌入模型: {self._model_name}")
            self._model = SentenceTransformer(
                self._model_name, device=self._device
            )

            # 更新向量维度
            self._dimension = self._model.get_sentence_embedding_dimension()
            logger.info(f"嵌入模型加载成功, 向量维度: {self._dimension}")

        except ImportError:
            logger.error("sentence-transformers未安装，请运行: pip install sentence-transformers")
            raise
        except Exception as e:
            logger.error(f"嵌入模型加载失败: {e}")
            raise

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        show_progress_bar: bool = False,
        normalize_embeddings: bool = True,
        **kwargs,
    ) -> np.ndarray:
        """将文本转换为向量

        Args:
            texts: 单个文本或文本列表
            batch_size: 批处理大小
            show_progress_bar: 是否显示进度条
            normalize_embeddings: 是否归一化向量
            **kwargs: 额外参数

        Returns:
            向量或向量矩阵
        """
        self._load_model()

        # 处理单个文本
        if isinstance(texts, str):
            texts = [texts]
            single = True
        else:
            single = False

        # 编码
        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=normalize_embeddings,
            **kwargs,
        )

        # 返回单个向量或向量矩阵
        if single:
            return embeddings[0]
        return embeddings

    def get_dimension(self) -> int:
        """获取向量维度

        Returns:
            向量维度
        """
        self._load_model()
        return self._dimension


class EmbeddingFactory:
    """嵌入模型工厂"""

    _instance: Optional[BaseEmbedding] = None

    @classmethod
    def get_embedding(cls, **kwargs) -> BaseEmbedding:
        """获取嵌入模型实例

        Args:
            **kwargs: 传递给嵌入模型的参数

        Returns:
            嵌入模型实例
        """
        if cls._instance is None:
            cls._instance = SentenceTransformerEmbedding(**kwargs)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """重置实例（用于测试）"""
        cls._instance = None
