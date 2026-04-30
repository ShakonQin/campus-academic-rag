"""检索调度专家Agent"""

import time
from typing import Dict, Any, List

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.core.retriever.retrieval_engine import RetrievalEngine
from src.utils.logger import logger


class RetrieveAgent(BaseAgent):
    """检索调度专家Agent

    负责检索策略调度、多路归并执行、Top-K结果筛选。
    """

    AGENT_TYPE = AgentType.RETRIEVE

    def __init__(self, retrieval_engine: RetrievalEngine = None):
        """初始化检索Agent

        Args:
            retrieval_engine: 检索引擎实例
        """
        super().__init__()
        self.retrieval_engine = retrieval_engine or RetrievalEngine()

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行检索任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            检索结果响应
        """
        start_time = time.time()

        try:
            query = context.query
            if not query:
                return self._create_error_response("查询为空")

            # 获取过滤条件
            filter_metadata = kwargs.get("filter_metadata", context.metadata.get("filter"))

            # 执行检索
            results = self.retrieval_engine.retrieve(
                query=query,
                top_k=kwargs.get("top_k", 10),
                use_vector=kwargs.get("use_vector", True),
                use_keyword=kwargs.get("use_keyword", True),
                use_reranker=kwargs.get("use_reranker", True),
                filter_metadata=filter_metadata,
            )

            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "chunk_id": result.chunk_id,
                    "content": result.content,
                    "metadata": result.metadata,
                    "score": result.final_score,
                    "channels": result.retrieval_channels,
                })

            execution_time = time.time() - start_time

            return self._create_success_response(
                data={
                    "results": formatted_results,
                    "total": len(formatted_results),
                },
                message=f"检索完成，返回 {len(formatted_results)} 个结果",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"检索Agent执行失败: {e}")
            return self._create_error_response(str(e), execution_time)

    def build_indexes(self, chunks) -> None:
        """构建索引

        Args:
            chunks: 分片列表
        """
        self.retrieval_engine.build_indexes(chunks)
