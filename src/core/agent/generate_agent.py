"""校园场景生成专家Agent"""

import time
from typing import Dict, Any, List, Optional

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.config.settings import settings
from src.utils.logger import logger


class GenerateAgent(BaseAgent):
    """校园场景生成专家Agent

    负责贴合校园场景的回答生成，支持考点梳理、作业答疑、论文解读等。
    """

    AGENT_TYPE = AgentType.GENERATE

    def __init__(self):
        """初始化生成Agent"""
        super().__init__()
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
                logger.info("LLM客户端初始化成功")
            except Exception as e:
                logger.error(f"LLM客户端初始化失败: {e}")
                raise
        return self._llm_client

    def execute(self, context: AgentContext, **kwargs) -> AgentResponse:
        """执行生成任务

        Args:
            context: Agent上下文
            **kwargs: 额外参数

        Returns:
            生成结果响应
        """
        start_time = time.time()

        try:
            query = context.query
            retrieval_results = context.retrieval_results

            if not query:
                return self._create_error_response("查询为空")

            # 构建上下文
            context_text = self._build_context(retrieval_results)

            # 构建Prompt
            prompt = self._build_prompt(query, context_text)

            # 调用LLM生成回答
            answer = self._generate_answer(prompt)

            # 构建引用信息
            citations = self._extract_citations(retrieval_results)

            execution_time = time.time() - start_time

            return self._create_success_response(
                data={
                    "answer": answer,
                    "citations": citations,
                    "context_used": len(retrieval_results) > 0,
                },
                message="回答生成完成",
                execution_time=execution_time,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"生成Agent执行失败: {e}")
            return self._create_error_response(str(e), execution_time)

    def _build_context(self, retrieval_results: List[Dict[str, Any]]) -> str:
        """构建检索上下文

        Args:
            retrieval_results: 检索结果

        Returns:
            上下文文本
        """
        if not retrieval_results:
            return ""

        context_parts = []
        for i, result in enumerate(retrieval_results[:5], 1):  # 最多使用5个结果
            content = result.get("content", "")
            metadata = result.get("metadata", {})
            doc_name = metadata.get("doc_name", "未知文档")
            page = metadata.get("page_number", "")

            context_part = f"[文档{i}: {doc_name}"
            if page:
                context_part += f", 第{page}页"
            context_part += f"]\n{content}"
            context_parts.append(context_part)

        return "\n\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """构建生成Prompt

        Args:
            query: 用户查询
            context: 检索上下文

        Returns:
            Prompt文本
        """
        system_prompt = """你是一个校园学术助手，专门帮助学生和教师解答学术问题。

你的回答必须：
1. 100%基于提供的知识库内容，不得编造信息
2. 引用具体来源（文档名称、页码）
3. 使用清晰、专业的学术语言
4. 适当使用列表、步骤等格式化方式
5. 如果知识库中没有相关信息，明确告知用户"""

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

        return f"{system_prompt}\n\n{user_prompt}"

    def _generate_answer(self, prompt: str) -> str:
        """调用LLM生成回答

        Args:
            prompt: Prompt文本

        Returns:
            生成的回答
        """
        try:
            client = self._get_llm_client()
            response = client.chat.completions.create(
                model=settings.llm.llm_model,
                messages=[
                    {"role": "system", "content": "你是一个校园学术助手。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=settings.llm.llm_max_tokens,
                temperature=settings.llm.llm_temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            return f"抱歉，回答生成时出现错误：{str(e)}"

    def _extract_citations(self, retrieval_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取引用信息

        Args:
            retrieval_results: 检索结果

        Returns:
            引用列表
        """
        citations = []
        for i, result in enumerate(retrieval_results[:5], 1):
            metadata = result.get("metadata", {})
            citations.append({
                "index": i,
                "doc_name": metadata.get("doc_name", ""),
                "page_number": metadata.get("page_number", 0),
                "chunk_id": result.get("chunk_id", ""),
                "score": result.get("score", 0.0),
            })
        return citations
