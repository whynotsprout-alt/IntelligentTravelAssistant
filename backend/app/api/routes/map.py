"""地图服务API路由"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from ...models.schemas import (
    Location,
    POISearchResponse,
    RouteRequest,
    RouteResponse,
    WeatherResponse
)
from ...services.amap_service import get_amap_service

router = APIRouter(prefix="/map", tags=["地图服务"])

class StaticMapRequest(BaseModel):
    city: str = Field(default="", description="城市名称")
    points: list[Location] = Field(default_factory=list, description="地图点位")
    width: int = Field(default=900, ge=200, le=1600, description="图片宽度")
    height: int = Field(default=500, ge=200, le=1200, description="图片高度")
    zoom: int | None = Field(default=None, ge=3, le=18, description="缩放级别")


@router.get(
    "/poi",
    response_model=POISearchResponse,
    summary="搜索POI",
    description="根据关键词搜索POI(兴趣点)"
)
async def search_poi(
    keywords: str = Query(
        ...,
        description="搜索关键词",
        examples={"default": {"summary": "示例关键词", "value": "故宫"}},
    ),
    city: str = Query(
        ...,
        description="城市",
        examples={"default": {"summary": "示例城市", "value": "北京"}},
    ),
    citylimit: bool = Query(True, description="是否限制在城市范围内")
):
    """
    搜索POI
    
    Args:
        keywords: 搜索关键词
        city: 城市
        citylimit: 是否限制在城市范围内
        
    Returns:
        POI搜索结果
    """
    try:
        # 获取服务实例
        service = get_amap_service()
        
        # 搜索POI
        pois = service.search_poi(keywords, city, citylimit)
        
        return POISearchResponse(
            success=True,
            message="POI搜索成功",
            data=pois
        )
        
    except Exception as e:
        print(f"❌ POI搜索失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"POI搜索失败: {str(e)}"
        )


@router.get(
    "/weather",
    response_model=WeatherResponse,
    summary="查询天气",
    description="查询指定城市的天气信息"
)
async def get_weather(
    city: str = Query(
        ...,
        description="城市名称",
        examples={"default": {"summary": "示例城市", "value": "北京"}},
    )
):
    """
    查询天气
    
    Args:
        city: 城市名称
        
    Returns:
        天气信息
    """
    try:
        # 获取服务实例
        service = get_amap_service()
        
        # 查询天气
        weather_info = service.get_weather(city)
        
        return WeatherResponse(
            success=True,
            message="天气查询成功",
            data=weather_info
        )
        
    except Exception as e:
        print(f"❌ 天气查询失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"天气查询失败: {str(e)}"
        )


@router.post(
    "/route",
    response_model=RouteResponse,
    summary="规划路线",
    description="规划两点之间的路线"
)
async def plan_route(request: RouteRequest):
    """
    规划路线
    
    Args:
        request: 路线规划请求
        
    Returns:
        路线信息
    """
    try:
        # 获取服务实例
        service = get_amap_service()
        
        # 规划路线
        route_info = service.plan_route(
            origin_address=request.origin_address,
            destination_address=request.destination_address,
            origin_city=request.origin_city,
            destination_city=request.destination_city,
            route_type=request.route_type
        )
        
        return RouteResponse(
            success=True,
            message="路线规划成功",
            data=route_info
        )
        
    except Exception as e:
        print(f"❌ 路线规划失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"路线规划失败: {str(e)}"
        )

@router.post(
    "/static-map",
    summary="生成静态地图URL",
    description="根据点位生成高德静态地图URL（用于导出）"
)
async def build_static_map(request: StaticMapRequest):
    try:
        service = get_amap_service()
        url = service.build_static_map_url(
            points=request.points,
            city=request.city,
            width=request.width,
            height=request.height,
            zoom=request.zoom,
        )
        return {
            "success": True,
            "message": "静态地图URL生成成功",
            "data": {"map_url": url},
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"静态地图URL生成失败: {str(e)}"
        )

@router.post(
    "/static-map-image",
    summary="生成静态地图图片数据",
    description="根据点位生成高德静态地图并返回dataURL（用于前端导出稳定渲染）"
)
async def build_static_map_image(request: StaticMapRequest):
    try:
        service = get_amap_service()
        image_data_url = service.build_static_map_data_url(
            points=request.points,
            city=request.city,
            width=request.width,
            height=request.height,
            zoom=request.zoom,
        )
        if not image_data_url:
            raise ValueError("静态地图图片获取失败")
        return {
            "success": True,
            "message": "静态地图图片生成成功",
            "data": {"map_image_data_url": image_data_url},
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"静态地图图片生成失败: {str(e)}"
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查地图服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查服务是否可用
        service = get_amap_service()
        
        return {
            "status": "healthy",
            "service": "map-service",
            "mcp_initialized": service.mcp_tool is not None,
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )

