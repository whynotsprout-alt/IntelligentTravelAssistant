"""规划协调 Agent — 编排其余 Agent，并调用 LLM 生成行程（占位实现）。"""

from typing import Any

from app.agents.attractions import AttractionsSearchAgent
from app.agents.base import AgentContext
from app.agents.hotel import HotelRecommendationAgent
from app.agents.weather import WeatherQueryAgent


class PlanningCoordinationAgent:
    """
    Orchestrator: attractions → weather → hotels → merge / LLM plan.
    Replace with HelloAgents workflow + MCP LLM tool.
    """

    def __init__(self) -> None:
        self._attractions = AttractionsSearchAgent()
        self._weather = WeatherQueryAgent()
        self._hotels = HotelRecommendationAgent()

    async def run(self, ctx: AgentContext) -> dict[str, Any]:
        attractions = await self._attractions.run(ctx)
        weather = await self._weather.run(ctx)
        hotels = await self._hotels.run(ctx)

        # TODO: MCP -> LLM API 生成自然语言行程与每日活动
        plan_text = (
            f"基于 {ctx.destination} 的示例行程："
            f"结合天气与兴趣 {', '.join(ctx.interests) or '通用'} 安排游览与休息。"
        )

        return {
            "summary": plan_text,
            "attractions": attractions,
            "weather": weather,
            "hotels": hotels,
            "itinerary_stub": [
                {"day_index": 1, "title": "抵达与市区", "activities": ["入住酒店", "地标打卡"]},
            ],
        }
