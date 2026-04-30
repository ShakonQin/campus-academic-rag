"""迭代优化专家Agent"""

import time
from typing import Dict, Any, List
from datetime import datetime

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.utils.logger import logger


class IterateAgent(BaseAgent):
    """迭代优化专家Agent

    负责系统性能监控、用户反馈收集、参数优化、迭代需求评估。
    """

    AGENT_TYPE = AgentType.ITERATE

    def __init__(self):
        """初始化迭代Agent"""
        super().__init__()
        self._performance_history: List[Dict[str, Any]] = []
        self._feedback_history: List[Dict[str, Any]] = []

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行迭代优化任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            优化结果响应
        """
        start_time = time.time()

        try:
            action = kwargs.get("action", "analyze")

            if action == "analyze":
                result = self._analyze_performance()
            elif action == "feedback":
                result = self._process_feedback(kwargs.get("feedback", {}))
            elif action == "optimize":
                result = self._suggest_optimizations()
            else:
                return self._create_error_response(f"未知操作: {action}")

            execution_time = time.time() - start_time

            return self._create_success_response(
                data=result,
                message="迭代分析完成",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"迭代Agent执行失败: {e}")
            return self._create_error_response(str(e), execution_time)

    def _analyze_performance(self) -> Dict[str, Any]:
        """分析系统性能

        Returns:
            性能分析结果
        """
        # 这里应该从监控系统获取实际数据
        # 目前返回示例数据
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "avg_response_time": 2.5,
                "retrieval_accuracy": 0.85,
                "hallucination_rate": 0.03,
                "user_satisfaction": 0.9,
            },
            "bottlenecks": [],
            "recommendations": [],
        }

        # 分析瓶颈
        if analysis["metrics"]["avg_response_time"] > 3.0:
            analysis["bottlenecks"].append("响应时间过长")
            analysis["recommendations"].append("优化检索策略，减少召回数量")

        if analysis["metrics"]["retrieval_accuracy"] < 0.9:
            analysis["bottlenecks"].append("检索准确率不足")
            analysis["recommendations"].append("调整向量和关键词权重，增加重排序")

        return analysis

    def _process_feedback(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """处理用户反馈

        Args:
            feedback: 用户反馈

        Returns:
            处理结果
        """
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "rating": feedback.get("rating", 0),
            "comment": feedback.get("comment", ""),
            "query": feedback.get("query", ""),
            "issue_type": feedback.get("issue_type", "other"),
        }

        self._feedback_history.append(feedback_entry)

        # 分析反馈
        analysis = {
            "total_feedback": len(self._feedback_history),
            "avg_rating": self._calculate_avg_rating(),
            "common_issues": self._identify_common_issues(),
            "latest_feedback": feedback_entry,
        }

        return analysis

    def _suggest_optimizations(self) -> Dict[str, Any]:
        """建议优化方案

        Returns:
            优化建议
        """
        suggestions = {
            "timestamp": datetime.now().isoformat(),
            "short_term": [],
            "medium_term": [],
            "long_term": [],
        }

        # 短期优化建议
        suggestions["short_term"] = [
            "调整检索Top-K值",
            "优化BM25和向量检索权重",
            "增加重排序模型",
        ]

        # 中期优化建议
        suggestions["medium_term"] = [
            "引入HyDE假设文档增强",
            "实现RAG-Fusion融合检索",
            "优化分片策略",
        ]

        # 长期优化建议
        suggestions["long_term"] = [
            "集成专业重排序模型",
            "实现Self-RAG自我反思",
            "建立用户反馈闭环",
        ]

        return suggestions

    def _calculate_avg_rating(self) -> float:
        """计算平均评分"""
        if not self._feedback_history:
            return 0.0
        ratings = [f["rating"] for f in self._feedback_history if f["rating"] > 0]
        return sum(ratings) / len(ratings) if ratings else 0.0

    def _identify_common_issues(self) -> List[str]:
        """识别常见问题"""
        if not self._feedback_history:
            return []

        issue_counts = {}
        for feedback in self._feedback_history:
            issue_type = feedback.get("issue_type", "other")
            issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1

        # 返回出现频率最高的问题
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:3]]

    def record_performance(self, metrics: Dict[str, Any]) -> None:
        """记录性能指标

        Args:
            metrics: 性能指标
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            **metrics,
        }
        self._performance_history.append(entry)

        # 保留最近1000条记录
        if len(self._performance_history) > 1000:
            self._performance_history = self._performance_history[-1000:]
