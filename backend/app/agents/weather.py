"""天气查询 Agent — 通过 MCP 调用高德或气象相关 API（占位实现）。"""

from typing import Any

from app.agents.base import AgentContext


class WeatherQueryAgent:
    """Weather along the trip window."""

    async def run(self, ctx: AgentContext) -> dict[str, Any]:
        # TODO: MCP -> 高德天气 / 第三方气象
        return {
            "source": "weather_stub",
            "days": [
                {
                    "date": ctx.start_date_iso,
                    "summary": "晴转多云（示例）",
                    "temp_high_c": 22.0,
                    "temp_low_c": 14.0,
                }
            ],
        }
