"""行程相关端点。"""

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import TripPlanRequest, TripPlanResponse
from app.services.trip_service import TripPlanningService

router = APIRouter()
_service = TripPlanningService()


@router.post("/trips/plan", response_model=TripPlanResponse)
async def plan_trip(body: TripPlanRequest) -> TripPlanResponse:
    if body.end_date < body.start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be on or after start_date",
        )
    return await _service.plan_trip(body)
