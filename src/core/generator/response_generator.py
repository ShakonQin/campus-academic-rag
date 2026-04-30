"""回答生成引擎"""

import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from src.core.retriever.multi_way_merge import RetrievalResult
from src.core.generator.citation_tracker import CitationTracker, Citation
from src.config.settings import settings
from src.utils.logger import logger


@dataclass
class GeneratedResponse:
    """生成的回答"""
    answer: str = ""
    citations: List[Citation] = field(default_factory=list)
    confidence: float = 0.0
    context_used: bool = False
    generation_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "answer": self.answer,
            "citations": [c.to_dict() for c in self.citations],
            "confidence": self.confidence,
            "context_used": self.context_used,
            "generation_time": self.generation_time,
        }


class ResponseGenerator:
    """回答生成器

    基于检索结果生成回答，支持引用溯源。
    """

    def __init__(self, citation_tracker: CitationTracker = None):
        """初始化回答生成器

        Args:
            citation_tracker: 引用追踪器
        """
        self.citation_tracker = citation_tracker or CitationTracker()
        self._llm_client = None

    def _get_llm_client(self):
        """获取LLM客户端"""
        if self._llm_client is None:
            try:
                import openai
                self._llm_client = openai.OpenAI(
                    api_key=settings.llm.llm_api_key,
                    base_url=settings.llm.llm_base_url,
                )
            except Exception as e:
                logger.error(f"LLM客户端初始化失败: {e}")
                raise
        return self._llm_client

    def generate(
        self,
        query: str,
        retrieval_results: List[RetrievalResult],
        scene_type: str = "general",
        history: List[Dict[str, str]] = None,
    ) -> GeneratedResponse:
        """生成回答

        Args:
            query: 用户查询
            retrieval_results: 检索结果
            scene_type: 场景类型（general/exam/homework/paper）
            history: 对话历史

        Returns:
            生成的回答
        """
        start_time = time.time()

        # 追踪引用
        self.citation_tracker.track_retrieval(retrieval_results)

        # 构建上下文
        context = self._build_context(retrieval_results)

        # 构建Prompt
        prompt = self._build_prompt(query, context, scene_type, history)

        # 生成回答
        answer = self._generate_answer(prompt)

        # 处理引用标记
        answer_with_citations = self._process_citations(answer, retrieval_results)

        generation_time = time.time() - start_time

        return GeneratedResponse(
            answer=answer_with_citations,
            citations=self.citation_tracker.get_citations(),
            confidence=self._calculate_confidence(retrieval_results),
            context_used=len(retrieval_results) > 0,
            generation_time=generation_time,
        )

    def _build_context(self, retrieval_results: List[RetrievalResult]) -> str:
        """构建检索上下文

        Args:
            retrieval_results: 检索结果

        Returns:
            上下文文本
        """
        if not retrieval_results:
            return ""

        context_parts = []
        for i, result in enumerate(retrieval_results[:5], 1):
            metadata = result.metadata
            doc_name = metadata.get("doc_name", "未知文档")
            page = metadata.get("page_number", "")

            context_part = f"[来源{i}: {doc_name}"
            if page:
                context_part += f", 第{page}页"
            context_part += f"]\n{result.content}"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        scene_type: str,
        history: List[Dict[str, str]] = None,
    ) -> str:
        """构建生成Prompt

        Args:
            query: 用户查询
            context: 检索上下文
            scene_type: 场景类型
            history: 对话历史

        Returns:
            Prompt文本
        """
        # 场景特定的系统提示
        scene_prompts = {
            "general": "你是一个校园学术助手，帮助学生和教师解答学术问题。",
            "exam": "你是一个考试辅导助手，帮助学生梳理考点、总结重点。",
            "homework": "你是一个作业辅导助手，帮助学生理解题目、提供解题思路。",
            "paper": "你是一个论文研读助手，帮助研究人员理解论文内容、提取关键信息。",
        }

        system_prompt = scene_prompts.get(scene_type, scene_prompts["general"])

        system_prompt += """

你的回答必须遵循以下原则：
1. 100%基于提供的知识库内容，不得编造信息
2. 每个关键知识点都要标注引用来源，格式：[来源N]
3. 使用清晰、专业的学术语言
4. 适当使用列表、步骤等格式化方式
5. 如果知识库中没有相关信息，明确告知用户"""

        # 构建消息
        messages = [{"role": "system", "content": system_prompt}]

        # 添加对话历史
        if history:
            for h in history[-3:]:  # 最近3轮对话
                messages.append({"role": "user", "content": h.get("query", "")})
                messages.append({"role": "assistant", "content": h.get("answer", "")})

        # 添加当前问题
        if context:
            user_prompt = f"""基于以下知识库内容回答问题：

【知识库内容】
{context}

【问题】
{query}

请提供准确、详细的回答，并标注引用来源。"""
        else:
            user_prompt = f"""【问题】
{query}

注意：知识库中未找到相关内容，请告知用户需要上传相关文档。"""

        messages.append({"role": "user", "content": user_prompt})

        return messages

    def _generate_answer(self, messages: List[Dict[str, str]]) -> str:
        """调用LLM生成回答

        Args:
            messages: 消息列表

        Returns:
            生成的回答
        """
        try:
            client = self._get_llm_client()
            response = client.chat.completions.create(
                model=settings.llm.llm_model,
                messages=messages,
                max_tokens=settings.llm.llm_max_tokens,
                temperature=settings.llm.llm_temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"抱歉，回答生成时出现错误：{str(e)}"

    def _process_citations(
        self,
        answer: str,
        retrieval_results: List[RetrievalResult],
    ) -> str:
        """处理引用标记

        Args:
            answer: 原始回答
            retrieval_results: 检索结果

        Returns:
            处理后的回答
        """
        import re

        # 替换引用标记为可点击的格式
        for i, result in enumerate(retrieval_results[:5], 1):
            pattern = f"[来源{i}]"
            if pattern in answer:
                metadata = result.metadata
                doc_name = metadata.get("doc_name", "")
                page = metadata.get("page_number", "")
                replacement = f"[{doc_name}"
                if page:
                    replacement += f" p.{page}"
                replacement += "]"
                answer = answer.replace(pattern, replacement)

        return answer

    def _calculate_confidence(self, retrieval_results: List[RetrievalResult]) -> float:
        """计算回答置信度

        Args:
            retrieval_results: 检索结果

        Returns:
            置信度分数
        """
        if not retrieval_results:
            return 0.0

        # 基于检索结果的相似度计算置信度
        scores = [r.final_score for r in retrieval_results[:3]]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # 归一化到0-1范围
        return min(avg_score * 1.2, 1.0)
