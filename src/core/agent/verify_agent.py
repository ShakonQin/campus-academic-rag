"""知识校验专家Agent"""

import time
from typing import Dict, Any, List

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.utils.logger import logger


class VerifyAgent(BaseAgent):
    """知识校验专家Agent

    负责校验生成内容与检索文档的一致性、识别幻觉、核对知识点准确性。
    """

    AGENT_TYPE = AgentType.VERIFY

    def __init__(self):
        """初始化校验Agent"""
        super().__init__()

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行校验任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            校验结果响应
        """
        start_time = time.time()

        try:
            answer = context.generated_answer
            retrieval_results = context.retrieval_results

            if not answer:
                return self._create_error_response("没有需要校验的回答")

            # 执行校验
            verification_result = self._verify_answer(answer, retrieval_results)

            execution_time = time.time() - start_time

            return self._create_success_response(
                data={
                    "verification": verification_result,
                },
                message=f"校验完成，可信度: {verification_result['confidence']:.1%}",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"校验Agent执行失败: {e}")
            return self._create_error_response(str(e), execution_time)

    def _verify_answer(
        self,
        answer: str,
        retrieval_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """校验回答

        Args:
            answer: 生成的回答
            retrieval_results: 检索结果

        Returns:
            校验结果
        """
        # 提取知识库内容
        knowledge_base = self._extract_knowledge(retrieval_results)

        # 执行各项检查
        checks = {
            "factual_consistency": self._check_factual_consistency(answer, knowledge_base),
            "citation_accuracy": self._check_citation_accuracy(answer, retrieval_results),
            "hallucination_detection": self._check_hallucination(answer, knowledge_base),
            "completeness": self._check_completeness(answer, knowledge_base),
        }

        # 计算总体可信度
        confidence = self._calculate_confidence(checks)

        # 生成校验报告
        report = self._generate_report(checks, confidence)

        return {
            "confidence": confidence,
            "checks": checks,
            "report": report,
            "passed": confidence >= 0.7,
        }

    def _extract_knowledge(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """提取知识库内容

        Args:
            retrieval_results: 检索结果

        Returns:
            知识库内容
        """
        contents = [result.get("content", "") for result in retrieval_results]
        return " ".join(contents)

    def _check_factual_consistency(self, answer: str, knowledge: str) -> Dict[str, Any]:
        """检查事实一致性

        Args:
            answer: 回答
            knowledge: 知识库内容

        Returns:
            检查结果
        """
        # 简单的关键词重叠检查
        import jieba

        answer_tokens = set(jieba.cut(answer))
        knowledge_tokens = set(jieba.cut(knowledge))

        # 移除停用词
        stopwords = {"的", "了", "是", "在", "和", "有", "就", "不", "也", "都", "这", "那"}
        answer_tokens -= stopwords
        knowledge_tokens -= stopwords

        if not answer_tokens:
            return {"score": 0.0, "detail": "回答为空"}

        overlap = len(answer_tokens & knowledge_tokens)
        score = overlap / len(answer_tokens) if answer_tokens else 0.0

        return {
            "score": min(score * 1.5, 1.0),  # 放大但限制在1.0
            "detail": f"关键词重叠率: {score:.1%}",
        }

    def _check_citation_accuracy(
        self,
        answer: str,
        retrieval_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """检查引用准确性

        Args:
            answer: 回答
            retrieval_results: 检索结果

        Returns:
            检查结果
        """
        # 检查是否包含引用标记
        import re

        citation_patterns = [
            r"\[文档\d+\]",
            r"第\d+页",
            r"文档.*?指出",
            r"根据.*?资料",
        ]

        has_citations = any(re.search(p, answer) for p in citation_patterns)

        return {
            "score": 0.8 if has_citations else 0.4,
            "detail": "包含引用" if has_citations else "未发现明确引用",
            "has_citations": has_citations,
        }

    def _check_hallucination(self, answer: str, knowledge: str) -> Dict[str, Any]:
        """检测幻觉

        Args:
            answer: 回答
            knowledge: 知识库内容

        Returns:
            检查结果
        """
        # 检查回答中是否包含知识库中没有的具体信息
        import re

        # 检查数字
        answer_numbers = set(re.findall(r"\d+", answer))
        knowledge_numbers = set(re.findall(r"\d+", knowledge))

        # 检查不在知识库中的数字
        unsupported_numbers = answer_numbers - knowledge_numbers

        # 检查专有名词（简化版）
        hallucination_score = 1.0 - (len(unsupported_numbers) * 0.1)
        hallucination_score = max(0.0, min(1.0, hallucination_score))

        return {
            "score": hallucination_score,
            "detail": f"发现{len(unsupported_numbers)}个未验证的数据",
            "unsupported_numbers": list(unsupported_numbers)[:5],
        }

    def _check_completeness(self, answer: str, knowledge: str) -> Dict[str, Any]:
        """检查完整性

        Args:
            answer: 回答
            knowledge: 知识库内容

        Returns:
            检查结果
        """
        # 检查回答长度是否合理
        answer_length = len(answer)
        knowledge_length = len(knowledge)

        if answer_length < 50:
            score = 0.3
            detail = "回答过短"
        elif knowledge_length > 0 and answer_length / knowledge_length > 2:
            score = 0.5
            detail = "回答可能过于冗长"
        else:
            score = 0.8
            detail = "回答长度适中"

        return {
            "score": score,
            "detail": detail,
        }

    def _calculate_confidence(self, checks: Dict[str, Dict[str, Any]]) -> float:
        """计算总体可信度

        Args:
            checks: 各项检查结果

        Returns:
            可信度分数
        """
        weights = {
            "factual_consistency": 0.35,
            "citation_accuracy": 0.25,
            "hallucination_detection": 0.30,
            "completeness": 0.10,
        }

        total_score = 0.0
        total_weight = 0.0

        for check_name, weight in weights.items():
            if check_name in checks:
                total_score += checks[check_name]["score"] * weight
                total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.0

    def _generate_report(self, checks: Dict[str, Dict[str, Any]], confidence: float) -> str:
        """生成校验报告

        Args:
            checks: 各项检查结果
            confidence: 可信度

        Returns:
            报告文本
        """
        report_parts = [f"校验报告 - 总体可信度: {confidence:.1%}"]
        report_parts.append("-" * 40)

        check_names = {
            "factual_consistency": "事实一致性",
            "citation_accuracy": "引用准确性",
            "hallucination_detection": "幻觉检测",
            "completeness": "完整性",
        }

        for check_name, check_result in checks.items():
            display_name = check_names.get(check_name, check_name)
            score = check_result["score"]
            detail = check_result["detail"]
            status = "✓" if score >= 0.7 else "△" if score >= 0.5 else "✗"
            report_parts.append(f"{status} {display_name}: {score:.1%} - {detail}")

        if confidence >= 0.8:
            report_parts.append("\n结论: 回答可信度高，可以使用")
        elif confidence >= 0.6:
            report_parts.append("\n结论: 回答基本可信，建议用户核实关键信息")
        else:
            report_parts.append("\n结论: 回答可信度较低，建议重新检索或人工审核")

        return "\n".join(report_parts)
