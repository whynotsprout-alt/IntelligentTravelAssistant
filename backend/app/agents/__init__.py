"""
HelloAgents 智能体层：任务分解、工具调用（MCP）、结果整合。

各 Agent 通过 MCP 调用外部 API（高德 / Unsplash / LLM）；此处为框架占位，接入时替换为真实 HelloAgents 运行时。
"""

from app.agents.attractions import AttractionsSearchAgent
from app.agents.hotel import HotelRecommendationAgent
from app.agents.planning_coordination import PlanningCoordinationAgent
from app.agents.weather import WeatherQueryAgent

__all__ = [
    "AttractionsSearchAgent",
    "WeatherQueryAgent",
    "HotelRecommendationAgent",
    "PlanningCoordinationAgent",
]
