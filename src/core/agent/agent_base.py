"""Agent基类"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from src.utils.logger import logger


class AgentType(Enum):
    """Agent类型枚举"""
    PARSE = "parse"  # 文档解析专家
    RETRIEVE = "retrieve"  # 检索调度专家
    VERIFY = "verify"  # 知识校验专家
    GENERATE = "generate"  # 校园场景生成专家
    ITERATE = "iterate"  # 系统迭代优化专家


@dataclass
class AgentContext:
    """Agent上下文"""
    query: str = ""  # 用户查询
    doc_id: str = ""  # 文档ID
    doc_path: str = ""  # 文档路径
    retrieval_results: List[Dict[str, Any]] = field(default_factory=list)  # 检索结果
    generated_answer: str = ""  # 生成的回答
    verification_result: Dict[str, Any] = field(default_factory=dict)  # 校验结果
    metadata: Dict[str, Any] = field(default_factory=dict)  # 其他元数据
    history: List[Dict[str, str]] = field(default_factory=list)  # 对话历史

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "query": self.query,
            "doc_id": self.doc_id,
            "doc_path": self.doc_path,
            "retrieval_results": self.retrieval_results,
            "generated_answer": self.generated_answer,
            "verification_result": self.verification_result,
            "metadata": self.metadata,
            "history": self.history,
        }


@dataclass
class AgentResponse:
    """Agent响应"""
    agent_type: AgentType
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "agent_type": self.agent_type.value,
            "success": self.success,
            "data": self.data,
            "message": self.message,
            "error": self.error,
            "execution_time": self.execution_time,
        }


class BaseAgent(ABC):
    """Agent基类"""

    AGENT_TYPE: AgentType = None

    def __init__(self, name: str = None):
        """初始化Agent

        Args:
            name: Agent名称
        """
        self.name = name or self.__class__.__name__
        self._initialized = False

    @abstractmethod
    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行Agent任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            Agent响应
        """
        pass

    def initialize(self) -> None:
        """初始化Agent资源"""
        if not self._initialized:
            logger.info(f"Agent [{self.name}] 初始化完成")
            self._initialized = True

    def cleanup(self) -> None:
        """清理Agent资源"""
        logger.debug(f"Agent [{self.name}] 资源清理完成")

    def _create_success_response(
        self,
        data: Dict[str, Any] = None,
        message: str = "",
        execution_time: float = 0.0,
    ) -> AgentResponse:
        """创建成功响应

        Args:
            data: 响应数据
            message: 响应消息
            execution_time: 执行时间

        Returns:
            成功响应
        """
        return AgentResponse(
            agent_type=self.AGENT_TYPE,
            success=True,
            data=data or {},
            message=message,
            execution_time=execution_time,
        )

    def _create_error_response(
        self,
        error: str,
        execution_time: float = 0.0,
    ) -> AgentResponse:
        """创建错误响应

        Args:
            error: 错误信息
            execution_time: 执行时间

        Returns:
            错误响应
        """
        return AgentResponse(
            agent_type=self.AGENT_TYPE,
            success=False,
            error=error,
            execution_time=execution_time,
        )
