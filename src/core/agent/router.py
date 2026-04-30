"""门控路由模块"""

from typing import Dict, Any, Optional, List, Type
import re

from src.core.agent.agent_base import BaseAgent, AgentType, AgentContext, AgentResponse
from src.utils.logger import logger


class AgentRouter:
    """Agent路由器

    基于用户问题类型、场景，自动激活对应的专家Agent。
    类MoE的稀疏激活机制。
    """

    def __init__(self):
        """初始化路由器"""
        self._agents: Dict[AgentType, BaseAgent] = {}
        self._scene_patterns: Dict[str, List[AgentType]] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """注册Agent

        Args:
            agent: Agent实例
        """
        self._agents[agent.AGENT_TYPE] = agent
        logger.info(f"已注册Agent: {agent.name} ({agent.AGENT_TYPE.value})")

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """分析查询意图

        Args:
            query: 用户查询

        Returns:
            分析结果
        """
        query_lower = query.lower()

        # 关键词匹配规则
        patterns = {
            "document_parsing": [
                r"解析|处理|上传|导入",
                r"pdf|pptx|docx|文档",
            ],
            "retrieval": [
                r"搜索|查找|检索|找",
                r"什么是|是什么|解释|定义",
                r"哪一章|哪一页|哪里",
            ],
            "verification": [
                r"验证|核实|确认|检查",
                r"是否正确|对不对|准确吗",
            ],
            "generation": [
                r"总结|归纳|梳理|整理",
                r"解答|回答|解释|说明",
                r"考点|重点|习题|作业",
                r"论文|实验|报告",
            ],
            "iteration": [
                r"优化|改进|反馈|建议",
                r"性能|速度|准确率",
            ],
        }

        # 检测场景
        detected_scenes = []
        for scene, scene_patterns in patterns.items():
            for pattern in scene_patterns:
                if re.search(pattern, query_lower):
                    detected_scenes.append(scene)
                    break

        return {
            "scenes": detected_scenes,
            "query_length": len(query),
            "has_question": "?" in query or "？" in query,
        }

    def route(self, context: AgentContext) -> List[AgentType]:
        """路由到对应的Agent

        Args:
            context: Agent上下文

        Returns:
            需要激活的Agent类型列表
        """
        analysis = self._analyze_query(context.query)
        scenes = analysis["scenes"]

        activated_agents = []

        # 默认激活检索和生成Agent
        if not scenes:
            activated_agents = [AgentType.RETRIEVE, AgentType.GENERATE]
        else:
            # 根据场景激活Agent
            scene_agent_map = {
                "document_parsing": [AgentType.PARSE],
                "retrieval": [AgentType.RETRIEVE],
                "verification": [AgentType.RETRIEVE, AgentType.VERIFY],
                "generation": [AgentType.RETRIEVE, AgentType.GENERATE],
                "iteration": [AgentType.ITERATE],
            }

            for scene in scenes:
                if scene in scene_agent_map:
                    for agent_type in scene_agent_map[scene]:
                        if agent_type not in activated_agents:
                            activated_agents.append(agent_type)

        # 确保检索和生成Agent总是激活（用于问答场景）
        if AgentType.RETRIEVE not in activated_agents:
            activated_agents.append(AgentType.RETRIEVE)
        if AgentType.GENERATE not in activated_agents:
            activated_agents.append(AgentType.GENERATE)

        logger.debug(f"路由分析: scenes={scenes}, 激活Agent={[a.value for a in activated_agents]}")
        return activated_agents

    def execute_pipeline(
        self,
        context: AgentContext,
        agent_types: Optional[List[AgentType]] = None,
    ) -> AgentContext:
        """执行Agent管道

        Args:
            context: Agent上下文
            agent_types: 指定的Agent类型列表（可选）

        Returns:
            更新后的上下文
        """
        if agent_types is None:
            agent_types = self.route(context)

        # 按顺序执行Agent
        execution_order = [
            AgentType.PARSE,
            AgentType.RETRIEVE,
            AgentType.VERIFY,
            AgentType.GENERATE,
        ]

        for agent_type in execution_order:
            if agent_type in agent_types and agent_type in self._agents:
                agent = self._agents[agent_type]
                try:
                    logger.info(f"执行Agent: {agent.name}")
                    response = agent.execute(context)

                    # 更新上下文
                    self._update_context(context, response)

                except Exception as e:
                    logger.error(f"Agent [{agent.name}] 执行失败: {e}")

        return context

    def _update_context(self, context: AgentContext, response: AgentResponse) -> None:
        """更新上下文

        Args:
            context: Agent上下文
            response: Agent响应
        """
        if not response.success:
            return

        agent_type = response.agent_type
        data = response.data

        if agent_type == AgentType.RETRIEVE:
            context.retrieval_results = data.get("results", [])

        elif agent_type == AgentType.GENERATE:
            context.generated_answer = data.get("answer", "")

        elif agent_type == AgentType.VERIFY:
            context.verification_result = data.get("verification", {})

        # 记录到历史
        context.history.append({
            "agent": agent_type.value,
            "response": response.to_dict(),
        })

    def get_agent(self, agent_type: AgentType) -> Optional[BaseAgent]:
        """获取Agent实例

        Args:
            agent_type: Agent类型

        Returns:
            Agent实例
        """
        return self._agents.get(agent_type)
