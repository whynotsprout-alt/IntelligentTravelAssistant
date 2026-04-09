"""AMap service wrapper."""

from app.config import get_settings


class AMapService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def build_static_map_url(self, lng: float, lat: float, zoom: int = 12) -> str:
        key = self._settings.amap_web_service_key or "YOUR_AMAP_WEB_SERVICE_KEY"
        location = f"{lng:.6f},{lat:.6f}"
        return (
            "https://restapi.amap.com/v3/staticmap"
            f"?location={location}&zoom={zoom}&size=750*300&markers=mid,,A:{location}&key={key}"
        )
