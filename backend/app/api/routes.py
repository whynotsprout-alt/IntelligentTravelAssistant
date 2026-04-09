"""API 路由聚合。"""

from fastapi import APIRouter

from app.api import trip

api_router = APIRouter()


@api_router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


api_router.include_router(trip.router, tags=["trip"])
