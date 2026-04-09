"""Map related API routes."""

from fastapi import APIRouter, Query

from app.services.amap_service import AMapService

router = APIRouter()
amap_service = AMapService()


@router.get("/map/static")
async def static_map(
    lng: float = Query(..., description="Longitude"),
    lat: float = Query(..., description="Latitude"),
    zoom: int = Query(12, ge=3, le=18),
) -> dict[str, str]:
    return {"url": amap_service.build_static_map_url(lng=lng, lat=lat, zoom=zoom)}
