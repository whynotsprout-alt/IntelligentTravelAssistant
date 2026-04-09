"""酒店推荐 Agent — 通过 MCP 调用 Unsplash 等（占位：配图）。"""

from typing import Any

from app.agents.base import AgentContext


class HotelRecommendationAgent:
    """Hotel suggestions; Unsplash used for imagery in full implementation."""

    async def run(self, ctx: AgentContext) -> dict[str, Any]:
        # TODO: MCP -> 酒店数据源 + Unsplash 配图
        return {
            "source": "hotel_stub",
            "hotels": [
                {
                    "name": f"{ctx.destination} 精品酒店（示例）",
                    "area": "市中心",
                    "price_level": ctx.budget_hint or "中等",
                    "image_url": None,
                }
            ],
        }
