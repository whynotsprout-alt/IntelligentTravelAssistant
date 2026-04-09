"""Trip planning API routes."""

from fastapi import APIRouter, HTTPException, status

from app.agents.trip_planner_agent import TripPlannerAgent
from app.models.schemas import TripPlanRequest, TripPlanResponse

router = APIRouter()
planner = TripPlannerAgent()


@router.post("/trip/plan", response_model=TripPlanResponse)
async def plan_trip(body: TripPlanRequest) -> TripPlanResponse:
    if body.end_date < body.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be on or after start_date",
        )
    return await planner.plan(body)
