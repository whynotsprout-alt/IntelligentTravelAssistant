"""行程规划业务逻辑。"""

from datetime import date

from app.agents.base import AgentContext
from app.agents.planning_coordination import PlanningCoordinationAgent
from app.models.schemas import (
    AgentArtifact,
    HotelSuggestion,
    ItineraryDay,
    MapPoint,
    TripPlanRequest,
    TripPlanResponse,
    WeatherSnapshot,
)


class TripPlanningService:
    def __init__(self) -> None:
        self._planner = PlanningCoordinationAgent()

    async def plan_trip(self, req: TripPlanRequest) -> TripPlanResponse:
        ctx = AgentContext(
            destination=req.destination.strip(),
            start_date_iso=req.start_date.isoformat(),
            end_date_iso=req.end_date.isoformat(),
            interests=req.interests,
            party_size=req.party_size,
            budget_hint=req.budget_hint,
        )
        raw = await self._planner.run(ctx)

        itinerary = [
            ItineraryDay(
                day_index=item["day_index"],
                title=item["title"],
                activities=list(item.get("activities") or []),
            )
            for item in raw.get("itinerary_stub") or []
        ]

        map_points: list[MapPoint] = []
        for p in raw.get("attractions", {}).get("pois") or []:
            map_points.append(
                MapPoint(
                    name=str(p.get("name", "景点")),
                    lng=float(p.get("lng", 0)),
                    lat=float(p.get("lat", 0)),
                    kind="poi",
                )
            )

        weather: list[WeatherSnapshot] = []
        for w in raw.get("weather", {}).get("days") or []:
            d = w.get("date")
            if isinstance(d, str):
                weather.append(
                    WeatherSnapshot(
                        date=date.fromisoformat(d[:10]),
                        summary=str(w.get("summary", "")),
                        temp_high_c=w.get("temp_high_c"),
                        temp_low_c=w.get("temp_low_c"),
                    )
                )

        hotels: list[HotelSuggestion] = []
        for h in raw.get("hotels", {}).get("hotels") or []:
            hotels.append(
                HotelSuggestion(
                    name=str(h.get("name", "酒店")),
                    area=h.get("area"),
                    price_level=h.get("price_level"),
                    image_url=h.get("image_url"),
                )
            )

        artifacts = AgentArtifact(
            attractions=raw.get("attractions") or {},
            weather=raw.get("weather") or {},
            hotels=raw.get("hotels") or {},
        )

        return TripPlanResponse(
            destination=ctx.destination,
            summary=str(raw.get("summary", "")),
            itinerary=itinerary,
            map_points=map_points,
            weather=weather,
            hotels=hotels,
            artifacts=artifacts,
        )
