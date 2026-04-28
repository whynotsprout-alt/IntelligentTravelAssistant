"""高德地图服务封装（MCP + HTTP API）."""

from __future__ import annotations

import logging
import threading
import base64
from urllib.parse import urlencode
from typing import Any, Dict, List, Optional

import requests
from hello_agents.tools import MCPTool

from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

logger = logging.getLogger(__name__)

_amap_mcp_tool: Optional[MCPTool] = None
_amap_mcp_lock = threading.Lock()
_amap_service: Optional["AMapService"] = None
_amap_service_lock = threading.Lock()


def _get_amap_key() -> str:
    settings = get_settings()
    key = settings.amap_api_key
    if not key:
        raise ValueError("高德地图API Key未配置，请在.env中设置 AMAP_API_KEY")
    return key


def get_amap_mcp_tool() -> MCPTool:
    """获取共享的高德MCP工具实例（线程安全单例）."""
    global _amap_mcp_tool
    if _amap_mcp_tool is None:
        with _amap_mcp_lock:
            if _amap_mcp_tool is None:
                _amap_mcp_tool = MCPTool(
                    name="amap",
                    description="高德地图服务,支持POI搜索、路线规划、天气查询等功能",
                    server_command=["uvx", "amap-mcp-server"],
                    env={"AMAP_MAPS_API_KEY": _get_amap_key()},
                    auto_expand=True,
                )
                logger.info("高德地图MCP工具初始化成功")
    return _amap_mcp_tool


class AMapService:
    """高德地图服务封装类（给 API 路由使用）."""

    def __init__(self) -> None:
        self.api_key = _get_amap_key()
        self.base_url = "https://restapi.amap.com/v3"
        # 保留 MCPTool 给 Agent 场景复用，避免在健康检查等场景访问私有字段
        self.mcp_tool = get_amap_mcp_tool()

    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        try:
            response = requests.get(
                f"{self.base_url}/place/text",
                params={
                    "keywords": keywords,
                    "city": city,
                    "citylimit": "true" if citylimit else "false",
                    "key": self.api_key,
                    "offset": 20,
                    "output": "json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            pois = data.get("pois", [])
            result: List[POIInfo] = []
            for item in pois:
                location = item.get("location", "")
                if not location or "," not in location:
                    continue
                lng_str, lat_str = location.split(",", 1)
                try:
                    result.append(
                        POIInfo(
                            id=item.get("id", ""),
                            name=item.get("name", ""),
                            type=item.get("type", ""),
                            address=item.get("address", ""),
                            location=Location(longitude=float(lng_str), latitude=float(lat_str)),
                            tel=item.get("tel") or None,
                        )
                    )
                except ValueError:
                    continue
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("POI搜索失败: %s", exc)
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        try:
            response = requests.get(
                f"{self.base_url}/weather/weatherInfo",
                params={
                    "city": city,
                    "extensions": "all",
                    "key": self.api_key,
                    "output": "json",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            forecasts = (data.get("forecasts") or [{}])[0].get("casts", [])
            result: List[WeatherInfo] = []
            for cast in forecasts:
                result.append(
                    WeatherInfo(
                        date=cast.get("date"),
                        day_weather=cast.get("dayweather", ""),
                        night_weather=cast.get("nightweather", ""),
                        day_temp=cast.get("daytemp", 0),
                        night_temp=cast.get("nighttemp", 0),
                        wind_direction=cast.get("daywind", ""),
                        wind_power=cast.get("daypower", ""),
                    )
                )
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("天气查询失败: %s", exc)
            return []

    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        try:
            response = requests.get(
                f"{self.base_url}/geocode/geo",
                params={
                    "address": address,
                    "city": city or "",
                    "key": self.api_key,
                    "output": "json",
                },
                timeout=10,
            )
            response.raise_for_status()
            geocodes = response.json().get("geocodes", [])
            if not geocodes:
                return None
            location = geocodes[0].get("location", "")
            if not location or "," not in location:
                return None
            lng_str, lat_str = location.split(",", 1)
            return Location(longitude=float(lng_str), latitude=float(lat_str))
        except Exception as exc:  # noqa: BLE001
            logger.exception("地理编码失败: %s", exc)
            return None

    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking",
    ) -> Dict[str, Any]:
        try:
            origin = self.geocode(origin_address, origin_city)
            destination = self.geocode(destination_address, destination_city)
            if not origin or not destination:
                return {
                    "distance": 0,
                    "duration": 0,
                    "route_type": route_type,
                    "description": "无法解析起终点坐标",
                }

            endpoint_map = {
                "walking": "direction/walking",
                "driving": "direction/driving",
                "transit": "direction/transit/integrated",
            }
            endpoint = endpoint_map.get(route_type, "direction/walking")
            params: Dict[str, Any] = {
                "origin": f"{origin.longitude},{origin.latitude}",
                "destination": f"{destination.longitude},{destination.latitude}",
                "key": self.api_key,
                "output": "json",
            }
            if route_type == "transit":
                params["city"] = origin_city or destination_city or ""

            response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=10)
            response.raise_for_status()
            data = response.json().get("route", {})
            paths = data.get("paths", [])
            if not paths:
                transits = data.get("transits", [])
                if transits:
                    best = transits[0]
                    return {
                        "distance": float(best.get("distance", 0)),
                        "duration": int(best.get("duration", 0)),
                        "route_type": route_type,
                        "description": "路线规划成功",
                    }
                return {
                    "distance": 0,
                    "duration": 0,
                    "route_type": route_type,
                    "description": "未找到可用路线",
                }
            best = paths[0]
            return {
                "distance": float(best.get("distance", 0)),
                "duration": int(best.get("duration", 0)),
                "route_type": route_type,
                "description": "路线规划成功",
            }
        except Exception as exc:  # noqa: BLE001
            logger.exception("路线规划失败: %s", exc)
            return {
                "distance": 0,
                "duration": 0,
                "route_type": route_type,
                "description": f"路线规划失败: {exc}",
            }

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        try:
            response = requests.get(
                f"{self.base_url}/place/detail",
                params={
                    "id": poi_id,
                    "key": self.api_key,
                    "output": "json",
                },
                timeout=10,
            )
            response.raise_for_status()
            pois = response.json().get("pois", [])
            return pois[0] if pois else {}
        except Exception as exc:  # noqa: BLE001
            logger.exception("获取POI详情失败: %s", exc)
            return {}

    def build_static_map_url(
        self,
        points: List[Location],
        city: Optional[str] = None,
        width: int = 900,
        height: int = 500,
        zoom: Optional[int] = None,
    ) -> str:
        """
        构建高德静态地图 URL，用于导出图片/PDF 时稳定展示地图。
        """
        valid_points = [
            point
            for point in points
            if -180 <= point.longitude <= 180 and -90 <= point.latitude <= 90
        ]

        center: Optional[Location] = None
        if city:
            center = self.geocode(city, city)
        if not center and valid_points:
            avg_lng = sum(point.longitude for point in valid_points) / len(valid_points)
            avg_lat = sum(point.latitude for point in valid_points) / len(valid_points)
            center = Location(longitude=avg_lng, latitude=avg_lat)

        params: Dict[str, Any] = {
            "key": self.api_key,
            "size": f"{max(width, 200)}*{max(height, 200)}",
            "scale": 2,
        }
        if center:
            params["location"] = f"{center.longitude:.6f},{center.latitude:.6f}"
        if zoom is not None:
            params["zoom"] = max(3, min(int(zoom), 18))

        if valid_points:
            marker_parts = [
                f"mid,0x4CAF50,{idx + 1}:{point.longitude:.6f},{point.latitude:.6f}"
                for idx, point in enumerate(valid_points[:20])
            ]
            params["markers"] = "|".join(marker_parts)

            if len(valid_points) >= 2:
                path_points = ";".join(
                    f"{point.longitude:.6f},{point.latitude:.6f}" for point in valid_points
                )
                params["paths"] = f"8,0x1890ff,1,,0.8:{path_points}"

        query = urlencode(params, safe=":,;|*")
        return f"https://restapi.amap.com/v3/staticmap?{query}"

    def build_static_map_data_url(
        self,
        points: List[Location],
        city: Optional[str] = None,
        width: int = 900,
        height: int = 500,
        zoom: Optional[int] = None,
    ) -> Optional[str]:
        """
        拉取静态地图并转为 data URL，避免前端导出时受跨域与瓦片层影响。
        """
        try:
            static_url = self.build_static_map_url(
                points=points,
                city=city,
                width=width,
                height=height,
                zoom=zoom,
            )
            response = requests.get(static_url, timeout=10)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "image/png")
            encoded = base64.b64encode(response.content).decode("ascii")
            return f"data:{content_type};base64,{encoded}"
        except Exception as exc:  # noqa: BLE001
            logger.exception("构建静态地图dataURL失败: %s", exc)
            return None


# 向后兼容旧名字
AmapService = AMapService


def get_amap_service() -> AMapService:
    """获取高德地图服务实例(线程安全单例)."""
    global _amap_service
    if _amap_service is None:
        with _amap_service_lock:
            if _amap_service is None:
                _amap_service = AMapService()
    return _amap_service

