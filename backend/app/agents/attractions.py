"""景点搜索 Agent — 通过 MCP 调用高德地图 API（占位实现）。"""

from typing import Any

from app.agents.base import AgentContext


class AttractionsSearchAgent:
    """Finds POIs for the destination. Replace `run` body with HelloAgents + MCP tools."""

    async def run(self, ctx: AgentContext) -> dict[str, Any]:
        # TODO: MCP -> 高德地图 周边搜索 / 关键词搜索
        return {
            "source": "amap_stub",
            "pois": [
                {"name": f"{ctx.destination} 地标（示例）", "lng": 116.397_128, "lat": 39.916_527},
            ],
        }
