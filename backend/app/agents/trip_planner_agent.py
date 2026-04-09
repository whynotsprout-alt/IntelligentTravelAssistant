"""Trip planner agent orchestration."""

from datetime import date

try:
    from helloagents import SimpleAgent  # type: ignore
except Exception:  # pragma: no cover - fallback when package not installed yet
    class SimpleAgent:  # type: ignore[override]
        """Fallback base class to keep local skeleton runnable."""

        pass

from app.models.schemas import (
    AgentArtifact,
    HotelSuggestion,
    ItineraryDay,
    MapPoint,
    TripPlanRequest,
    TripPlanResponse,
    WeatherSnapshot,
)
from app.services.amap_service import AMapService
from app.services.llm_service import LLMService


class TripPlannerAgent(SimpleAgent):
    """HelloAgents-based planner (SimpleAgent style) with service orchestration."""

    def __init__(self) -> None:
        self._amap = AMapService()
        self._llm = LLMService()

    async def plan(self, req: TripPlanRequest) -> TripPlanResponse:
        summary = await self._llm.generate_trip_summary(req.destination, req.interests)
        itinerary = [
            ItineraryDay(
                day_index=1,
                title="抵达与城市初探",
                activities=["酒店入住", "城市地标打卡", "晚餐自由活动"],
            )
        ]
        map_points = [
            MapPoint(
                name=f"{req.destination} 中心地标",
                lng=116.397128,
                lat=39.916527,
                kind="poi",
            )
        ]
        weather = [
            WeatherSnapshot(
                date=req.start_date if isinstance(req.start_date, date) else date.today(),
                summary="晴转多云（示例）",
                temp_high_c=24,
                temp_low_c=15,
            )
        ]
        hotels = [
            HotelSuggestion(
                name=f"{req.destination} 精品酒店（示例）",
                area="市中心",
                price_level=req.budget_hint or "中等",
                image_url=None,
            )
        ]
        artifacts = AgentArtifact(
            attractions={"provider": "amap", "static_example": self._amap.build_static_map_url(116.397128, 39.916527)},
            weather={"provider": "stub"},
            hotels={"provider": "stub"},
        )

        return TripPlanResponse(
            destination=req.destination,
            summary=summary,
            itinerary=itinerary,
            map_points=map_points,
            weather=weather,
            hotels=hotels,
            artifacts=artifacts,
        )
