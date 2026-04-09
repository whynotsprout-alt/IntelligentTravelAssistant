"""Request/response schemas for trip planning."""

from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class TripPlanRequest(BaseModel):
    destination: str = Field(..., min_length=1, description="City or region name")
    start_date: date
    end_date: date
    budget_hint: str | None = None
    interests: list[str] = Field(default_factory=list)
    party_size: int = Field(default=1, ge=1, le=20)


class MapPoint(BaseModel):
    name: str
    lng: float
    lat: float
    kind: str = "poi"


class WeatherSnapshot(BaseModel):
    date: date
    summary: str
    temp_high_c: float | None = None
    temp_low_c: float | None = None


class HotelSuggestion(BaseModel):
    name: str
    area: str | None = None
    price_level: str | None = None
    image_url: str | None = None


class ItineraryDay(BaseModel):
    day_index: int
    title: str
    activities: list[str] = Field(default_factory=list)


class AgentArtifact(BaseModel):
    """Raw outputs from sub-agents (for debugging / UI detail)."""

    attractions: dict[str, Any] = Field(default_factory=dict)
    weather: dict[str, Any] = Field(default_factory=dict)
    hotels: dict[str, Any] = Field(default_factory=dict)


class TripPlanResponse(BaseModel):
    destination: str
    summary: str
    itinerary: list[ItineraryDay] = Field(default_factory=list)
    map_points: list[MapPoint] = Field(default_factory=list)
    weather: list[WeatherSnapshot] = Field(default_factory=list)
    hotels: list[HotelSuggestion] = Field(default_factory=list)
    artifacts: AgentArtifact | None = None
