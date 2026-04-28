"""多智能体旅行规划系统."""

import json
import logging
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import Any, Dict, Optional, Tuple

from hello_agents import SimpleAgent
from pydantic import ValidationError

from ..models.schemas import Attraction, Budget, DayPlan, Hotel, Location, Meal, TripPlan, TripRequest
from ..services.amap_service import get_amap_mcp_tool, get_amap_service
from ..services.llm_service import get_llm
from .prompts import (
    ATTRACTION_AGENT_PROMPT,
    HOTEL_AGENT_PROMPT,
    PLANNER_AGENT_PROMPT,
    WEATHER_AGENT_PROMPT,
)

logger = logging.getLogger(__name__)


class MultiAgentTripPlanner:
    """多智能体旅行规划系统."""

    def __init__(self):
        self.llm = get_llm()
        self.amap_tool = get_amap_mcp_tool()
        self.attraction_agent = SimpleAgent(
            name="景点搜索专家",
            llm=self.llm,
            system_prompt=ATTRACTION_AGENT_PROMPT,
        )
        self.attraction_agent.add_tool(self.amap_tool)

        self.weather_agent = SimpleAgent(
            name="天气查询专家",
            llm=self.llm,
            system_prompt=WEATHER_AGENT_PROMPT,
        )
        self.weather_agent.add_tool(self.amap_tool)

        self.hotel_agent = SimpleAgent(
            name="酒店推荐专家",
            llm=self.llm,
            system_prompt=HOTEL_AGENT_PROMPT,
        )
        self.hotel_agent.add_tool(self.amap_tool)

        self.planner_agent = SimpleAgent(
            name="行程规划专家",
            llm=self.llm,
            system_prompt=PLANNER_AGENT_PROMPT,
        )
        logger.info(
            "MultiAgentTripPlanner initialized: tools attraction=%d weather=%d hotel=%d",
            len(self.attraction_agent.list_tools()),
            len(self.weather_agent.list_tools()),
            len(self.hotel_agent.list_tools()),
        )

    def plan_trip(self, request: TripRequest) -> TripPlan:
        """使用多智能体协作生成旅行计划."""
        logger.info(
            "Start plan trip city=%s days=%s transport=%s accommodation=%s",
            request.city,
            request.travel_days,
            request.transportation,
            request.accommodation,
        )

        with ThreadPoolExecutor(max_workers=3) as executor:
            attraction_future = executor.submit(
                self._run_agent_step,
                "attraction",
                self.attraction_agent,
                self._build_attraction_query(request),
            )
            weather_future = executor.submit(
                self._run_agent_step,
                "weather",
                self.weather_agent,
                self._build_weather_query(request),
            )
            hotel_future = executor.submit(
                self._run_agent_step,
                "hotel",
                self.hotel_agent,
                self._build_hotel_query(request),
            )

            attraction_response, attraction_error = attraction_future.result()
            weather_response, weather_error = weather_future.result()
            hotel_response, hotel_error = hotel_future.result()

        errors = [err for err in [attraction_error, weather_error, hotel_error] if err]
        if errors:
            logger.warning("Sub-agents had partial failures: %s", errors)

        planner_query = self._build_planner_query(
            request=request,
            attractions=self._summarize_agent_output("景点", attraction_response),
            weather=self._summarize_agent_output("天气", weather_response),
            hotels=self._summarize_agent_output("酒店", hotel_response),
            step_errors=errors,
        )

        planner_response, planner_error = self._run_agent_step(
            "planner", self.planner_agent, planner_query
        )
        if planner_error:
            logger.error("Planner agent failed: %s", planner_error)
            return self._create_fallback_plan(request)

        try:
            trip_plan = self._parse_response(planner_response, request)
            self._apply_deterministic_budget(trip_plan, request)
            self._validate_budget_consistency(trip_plan)
            return trip_plan
        except Exception as exc:
            logger.exception("Planner response parse/validate failed: %s", exc)
            return self._create_fallback_plan(request)

    def _run_agent_step(
        self, step: str, agent: SimpleAgent, query: str
    ) -> Tuple[str, Optional[str]]:
        """执行一个子 Agent 步骤并返回(响应, 错误)."""
        try:
            response = agent.run(query)
            return response or "", None
        except Exception as exc:  # noqa: BLE001
            error = f"{step} step failed: {exc}"
            logger.exception(error)
            return "", error

    def _build_attraction_query(self, request: TripRequest) -> str:
        """构建景点搜索查询."""
        keywords = self._build_preference_keywords(request.preferences, fallback="景点")
        return (
            f"请调用amap_maps_text_search搜索{request.city}的景点。\n"
            f"关键词优先使用: {keywords}\n"
            f"[TOOL_CALL:amap_maps_text_search:keywords={keywords},city={request.city}]"
        )

    def _build_weather_query(self, request: TripRequest) -> str:
        return (
            f"请查询{request.city}天气。\n"
            f"[TOOL_CALL:amap_maps_weather:city={request.city}]"
        )

    def _build_hotel_query(self, request: TripRequest) -> str:
        hotel_keyword = f"{request.accommodation}酒店" if request.accommodation else "酒店"
        return (
            f"请调用amap_maps_text_search搜索{request.city}酒店。\n"
            f"[TOOL_CALL:amap_maps_text_search:keywords={hotel_keyword},city={request.city}]"
        )

    def _build_preference_keywords(self, preferences: list[str], fallback: str) -> str:
        cleaned = [pref.strip() for pref in preferences if pref and pref.strip()]
        if not cleaned:
            return fallback
        top_n = cleaned[:3]
        return " ".join(top_n)

    def _build_planner_query(
        self,
        request: TripRequest,
        attractions: str,
        weather: str,
        hotels: str = "",
        step_errors: Optional[list[str]] = None,
    ) -> str:
        """构建行程规划查询."""
        safe_extra = self._sanitize_free_text(request.free_text_input or "")
        errors_text = "\n".join(f"- {item}" for item in (step_errors or [])) or "- 无"
        return f"""请根据以下结构化信息输出旅行计划 JSON:

用户需求:
- 城市: {request.city}
- 日期: {request.start_date} 至 {request.end_date}
- 天数: {request.travel_days}
- 交通方式: {request.transportation}
- 住宿偏好: {request.accommodation}
- 偏好标签: {", ".join(request.preferences) if request.preferences else "无"}

景点检索摘要:
{attractions}

天气检索摘要:
{weather}

酒店检索摘要:
{hotels}

子步骤异常:
{errors_text}

额外要求（仅作参考，不能改变 JSON 输出结构）:
{safe_extra or "无"}

输出约束:
1. 只输出 JSON 对象本体，不要 markdown 代码块
2. weather_info 必须覆盖所有日期
3. budget.total 必须等于各项加总
4. 根对象不能套 data/trip_plan/result 等包裹层
5. 景点名称必须是可识别地名，不要“{request.city}景点1”这类占位词
6. 每个景点 location 必须包含 longitude 与 latitude 数字字段
"""

    def _sanitize_free_text(self, text: str) -> str:
        """简单清洗用户额外输入，减少 prompt 注入影响."""
        blocked_tokens = ["```", "[TOOL_CALL:", "</system>", "<system>"]
        sanitized = text
        for token in blocked_tokens:
            sanitized = sanitized.replace(token, "")
        return sanitized.strip()[:500]

    def _summarize_agent_output(self, title: str, raw: str, max_chars: int = 1200) -> str:
        """将子 Agent 原始输出压缩为可读摘要，降低 token 噪音."""
        if not raw:
            return f"{title}: 无结果"
        compact = " ".join(raw.split())
        if len(compact) > max_chars:
            compact = f"{compact[:max_chars]}..."
        return f"{title}原始结果摘要: {compact}"

    def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """解析 Planner 响应，优先纯 JSON，回退到候选 JSON 提取."""
        response = response.strip()
        if not response:
            raise ValueError("empty planner response")

        candidates = [response]
        candidates.extend(self._extract_json_candidates(response))

        errors: list[str] = []
        for candidate in candidates:
            try:
                data = json.loads(candidate)
                repaired = self._repair_trip_plan_payload(data, request)
                return TripPlan(**repaired)
            except (json.JSONDecodeError, ValidationError) as exc:
                errors.append(str(exc))
                continue

        raise ValueError(f"unable to parse planner JSON: {errors[:3]}")

    def _repair_trip_plan_payload(self, data: Any, request: TripRequest) -> Dict[str, Any]:
        """
        将 LLM 的松散结构修复为 TripPlan 标准结构。

        支持 data/trip_plan 包裹、itinerary 替代字段、对象/数组混排等常见偏差。
        """
        if not isinstance(data, dict):
            raise ValueError("planner payload must be JSON object")

        root = data
        for key in ("trip_plan", "data", "result", "output"):
            nested = root.get(key)
            if isinstance(nested, dict):
                root = nested
                break

        raw_days = root.get("days") or root.get("itinerary") or root.get("daily_plan") or []
        if isinstance(raw_days, dict):
            raw_days = list(raw_days.values())
        if not isinstance(raw_days, list):
            raw_days = []

        city_center = self._resolve_city_center(request.city)
        normalized_days: list[Dict[str, Any]] = []

        for idx, item in enumerate(raw_days):
            day = item if isinstance(item, dict) else {}
            normalized_days.append(
                self._normalize_day_payload(
                    day=day,
                    idx=idx,
                    request=request,
                    city_center=city_center,
                )
            )

        if not normalized_days:
            # 若规划结果完全不可用，直接回退到可展示的结构
            return self._create_fallback_plan(request).model_dump()

        return {
            "city": root.get("city") or root.get("destination") or request.city,
            "start_date": root.get("start_date") or request.start_date.isoformat(),
            "end_date": root.get("end_date") or request.end_date.isoformat(),
            "days": normalized_days,
            "weather_info": self._normalize_weather_payload(
                root.get("weather_info") or root.get("weather") or [],
                request=request,
            ),
            "overall_suggestions": root.get("overall_suggestions")
            or root.get("suggestions")
            or root.get("summary")
            or f"{request.city}{request.travel_days}日行程建议已生成，出发前请确认景区营业时间。",
            "budget": root.get("budget"),
        }

    def _normalize_day_payload(
        self,
        day: Dict[str, Any],
        idx: int,
        request: TripRequest,
        city_center: Location,
    ) -> Dict[str, Any]:
        date_value = day.get("date") or (request.start_date + timedelta(days=idx)).isoformat()
        attractions = day.get("attractions") or day.get("pois") or day.get("spots") or []
        meals = day.get("meals") or day.get("foods") or {}

        if isinstance(attractions, dict):
            attractions = list(attractions.values())
        if not isinstance(attractions, list):
            attractions = []

        if isinstance(meals, dict):
            meals = [
                {"type": meal_type, "name": meal_name}
                for meal_type, meal_name in meals.items()
                if meal_name
            ]
        if not isinstance(meals, list):
            meals = []

        normalized_attractions = [
            self._normalize_attraction_payload(item, request.city, city_center, idx, item_idx)
            for item_idx, item in enumerate(attractions[:3])
        ]
        if len(normalized_attractions) < 2:
            normalized_attractions.extend(
                [
                    item.model_dump()
                    for item in self._build_fallback_attractions_for_day(
                    city=request.city,
                    city_center=city_center,
                    day_idx=idx,
                    preferred_count=2 - len(normalized_attractions),
                )
                    ]
            )

        normalized_meals = [self._normalize_meal_payload(item) for item in meals if item]
        normalized_meals = self._ensure_three_meals(normalized_meals, day_idx=idx, city=request.city)

        return {
            "date": date_value,
            # 统一按数组顺序归一化为 0-based，避免 LLM 返回 1-based 造成“从第2天开始显示”
            "day_index": idx,
            "description": day.get("description")
            or day.get("theme")
            or f"第{idx + 1}天围绕{request.city}核心区域游览",
            "transportation": day.get("transportation") or request.transportation,
            "accommodation": day.get("accommodation") or request.accommodation,
            "hotel": self._normalize_hotel_payload(
                day.get("hotel")
                or day.get("recommended_hotel")
                or (day.get("hotels")[0] if isinstance(day.get("hotels"), list) and day.get("hotels") else None)
            ),
            "attractions": normalized_attractions,
            "meals": normalized_meals,
        }

    def _parse_day_index(self, value: Any, default: int) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r"\d+", value)
            if match:
                number = int(match.group())
                if "day" in value.lower() or ("第" in value and "天" in value):
                    return max(number - 1, 0)
                return number
        return default

    def _normalize_attraction_payload(
        self,
        attraction: Any,
        city: str,
        city_center: Location,
        day_idx: int,
        attraction_idx: int,
    ) -> Dict[str, Any]:
        item = attraction if isinstance(attraction, dict) else {"name": str(attraction)}
        location = self._normalize_location_payload(item.get("location"))
        if not location:
            location = self._build_offset_location(city_center, day_idx, attraction_idx)
        name = str(item.get("name") or "").strip()
        if not name or re.search(rf"^{re.escape(city)}景点\d+$", name):
            fallback_names = [
                f"{city}历史文化街区",
                f"{city}城市地标观景点",
                f"{city}特色生活街区",
            ]
            name = fallback_names[(day_idx + attraction_idx) % len(fallback_names)]
        return {
            "name": name,
            "address": item.get("address") or f"{city}市",
            "location": location.model_dump(),
            "visit_duration": item.get("visit_duration") or item.get("duration") or 120,
            "description": item.get("description") or f"推荐游览{city}代表性地标与街区",
            "category": item.get("category") or item.get("type") or "景点",
            "rating": item.get("rating"),
            "ticket_price": item.get("ticket_price") or item.get("price") or 0,
            "poi_id": item.get("poi_id") or item.get("id") or "",
            "image_url": item.get("image_url"),
        }

    def _normalize_meal_payload(self, meal: Any) -> Dict[str, Any]:
        item = meal if isinstance(meal, dict) else {"name": str(meal)}
        meal_type = str(item.get("type") or "").lower()
        if meal_type not in {"breakfast", "lunch", "dinner", "snack"}:
            meal_type = "snack"
        return {
            "type": meal_type,
            "name": item.get("name") or "特色餐饮",
            "address": item.get("address"),
            "description": item.get("description") or "",
            "estimated_cost": item.get("estimated_cost") or item.get("cost") or 0,
        }

    def _ensure_three_meals(
        self, meals: list[Dict[str, Any]], day_idx: int, city: str
    ) -> list[Dict[str, Any]]:
        meal_map: Dict[str, Dict[str, Any]] = {meal["type"]: meal for meal in meals if "type" in meal}
        defaults = {
            "breakfast": f"第{day_idx + 1}天早餐",
            "lunch": f"{city}特色午餐",
            "dinner": f"{city}风味晚餐",
        }
        result: list[Dict[str, Any]] = []
        for meal_type in ("breakfast", "lunch", "dinner"):
            if meal_type in meal_map:
                result.append(meal_map[meal_type])
            else:
                result.append(
                    {
                        "type": meal_type,
                        "name": defaults[meal_type],
                        "description": "可根据实时口味调整",
                        "estimated_cost": 0,
                    }
                )
        return result

    def _normalize_hotel_payload(self, hotel: Any) -> Optional[Dict[str, Any]]:
        if not hotel:
            return None
        item = hotel if isinstance(hotel, dict) else {"name": str(hotel)}
        if not item.get("name"):
            return None
        normalized = Hotel(
            name=item.get("name", ""),
            address=item.get("address", ""),
            location=self._normalize_location_payload(item.get("location")),
            price_range=item.get("price_range") or item.get("price") or "",
            rating=item.get("rating"),
            distance=item.get("distance") or "",
            type=item.get("type") or "酒店",
            estimated_cost=item.get("estimated_cost") or item.get("cost") or 0,
        )
        return normalized.model_dump()

    def _normalize_weather_payload(
        self, weather_payload: Any, request: TripRequest
    ) -> list[Dict[str, Any]]:
        if isinstance(weather_payload, dict):
            weather_payload = list(weather_payload.values())
        if not isinstance(weather_payload, list):
            weather_payload = []

        weather_by_date: Dict[str, Dict[str, Any]] = {}
        for idx, item in enumerate(weather_payload):
            entry = item if isinstance(item, dict) else {}
            date_value = entry.get("date") or (request.start_date + timedelta(days=idx)).isoformat()
            weather_by_date[date_value] = {
                "date": date_value,
                "day_weather": entry.get("day_weather") or entry.get("weather_day") or "多云",
                "night_weather": entry.get("night_weather") or entry.get("weather_night") or "晴",
                "day_temp": entry.get("day_temp") or entry.get("temp_day") or 26,
                "night_temp": entry.get("night_temp") or entry.get("temp_night") or 18,
                "wind_direction": entry.get("wind_direction") or entry.get("wind_dir") or "东北风",
                "wind_power": entry.get("wind_power") or entry.get("wind_level") or "3级",
            }

        # weather_info 必须覆盖每一天
        result: list[Dict[str, Any]] = []
        for idx in range(request.travel_days):
            date_value = (request.start_date + timedelta(days=idx)).isoformat()
            result.append(
                weather_by_date.get(
                    date_value,
                    {
                        "date": date_value,
                        "day_weather": "多云",
                        "night_weather": "晴",
                        "day_temp": 26,
                        "night_temp": 18,
                        "wind_direction": "东北风",
                        "wind_power": "3级",
                    },
                )
            )
        return result

    def _normalize_location_payload(self, location: Any) -> Optional[Location]:
        if isinstance(location, Location):
            return location
        if isinstance(location, str) and "," in location:
            lng_str, lat_str = location.split(",", 1)
            try:
                return Location(longitude=float(lng_str), latitude=float(lat_str))
            except ValueError:
                return None
        if isinstance(location, dict):
            lng = (
                location.get("longitude")
                or location.get("lng")
                or location.get("lon")
                or location.get("x")
            )
            lat = location.get("latitude") or location.get("lat") or location.get("y")
            if lng is not None and lat is not None:
                try:
                    return Location(longitude=float(lng), latitude=float(lat))
                except (TypeError, ValueError):
                    return None
        return None

    def _extract_json_candidates(self, text: str) -> list[str]:
        """从文本中提取所有可解码 JSON 对象候选."""
        decoder = json.JSONDecoder()
        candidates: list[str] = []
        idx = 0
        text_len = len(text)
        while idx < text_len:
            brace_pos = text.find("{", idx)
            if brace_pos < 0:
                break
            try:
                _, end = decoder.raw_decode(text[brace_pos:])
                candidates.append(text[brace_pos : brace_pos + end])
                idx = brace_pos + end
            except json.JSONDecodeError:
                idx = brace_pos + 1
        candidates.sort(key=len, reverse=True)
        return candidates

    def _validate_budget_consistency(self, plan: TripPlan) -> None:
        """校验预算总额一致性."""
        if not plan.budget:
            return
        parts = (
            plan.budget.total_attractions
            + plan.budget.total_hotels
            + plan.budget.total_meals
            + plan.budget.total_transportation
        )
        if plan.budget.total != parts:
            logger.warning(
                "Budget total mismatch: total=%s parts=%s",
                plan.budget.total,
                parts,
            )
            plan.budget.total = parts

    def _apply_deterministic_budget(self, plan: TripPlan, request: TripRequest) -> None:
        """基于结构化行程数据计算预算,覆盖/补全 LLM 估算."""
        accommodation_price_map = {
            "经济": 300,
            "舒适": 500,
            "豪华": 1000,
            "民宿": 400,
        }
        transportation_daily_map = {
            "公共交通": 50,
            "自驾": 180,
            "步行": 20,
            "混合": 100,
        }
        default_meal_cost = 60
        default_attraction_ticket = 60

        total_attractions = 0
        total_meals = 0
        total_hotels = 0

        for day in plan.days:
            for attraction in day.attractions:
                ticket_price = attraction.ticket_price or default_attraction_ticket
                total_attractions += max(ticket_price, 0)
            for meal in day.meals:
                meal_cost = meal.estimated_cost or default_meal_cost
                total_meals += max(meal_cost, 0)
            if day.hotel:
                hotel_cost = day.hotel.estimated_cost or 0
                total_hotels += max(hotel_cost, 0)

        # 如果日程中没有酒店估算值,用住宿偏好做兜底估算(按晚计费)
        if total_hotels == 0:
            nightly_cost = 500
            for keyword, value in accommodation_price_map.items():
                if keyword in (request.accommodation or ""):
                    nightly_cost = value
                    break
            total_hotels = nightly_cost * max(request.travel_days - 1, 1)

        daily_transport = transportation_daily_map.get(request.transportation, 80)
        total_transportation = daily_transport * max(request.travel_days, 1)

        total = total_attractions + total_hotels + total_meals + total_transportation
        plan.budget = Budget(
            total_attractions=total_attractions,
            total_hotels=total_hotels,
            total_meals=total_meals,
            total_transportation=total_transportation,
            total=total,
        )

    def _create_fallback_plan(self, request: TripRequest) -> TripPlan:
        """创建备用计划(当 Agent 失败时)."""
        start_date = request.start_date
        city_center = self._resolve_city_center(request.city)
        days = []
        for i in range(request.travel_days):
            current_date = start_date + timedelta(days=i)
            attractions = self._build_fallback_attractions_for_day(
                city=request.city,
                city_center=city_center,
                day_idx=i,
                preferred_count=2,
                preferences=request.preferences,
            )
            day_plan = DayPlan(
                date=current_date,
                day_index=i,
                description=f"第{i + 1}天行程",
                transportation=request.transportation,
                accommodation=request.accommodation,
                attractions=attractions,
                meals=[
                    Meal(
                        type="breakfast",
                        name=f"第{i + 1}天早餐",
                        description="当地特色早餐",
                    ),
                    Meal(type="lunch", name=f"第{i + 1}天午餐", description="午餐推荐"),
                    Meal(type="dinner", name=f"第{i + 1}天晚餐", description="晚餐推荐"),
                ],
            )
            days.append(day_plan)

        plan = TripPlan(
            city=request.city,
            start_date=request.start_date,
            end_date=request.end_date,
            days=days,
            weather_info=[],
            overall_suggestions=f"这是为您规划的{request.city}{request.travel_days}日游行程，建议提前查看开放时间。",
        )
        self._apply_deterministic_budget(plan, request)
        return plan

    def _resolve_city_center(self, city: str) -> Location:
        """优先通过地理编码获取城市中心点，失败时使用可重复计算的偏移点。"""
        try:
            amap_service = get_amap_service()
            center = amap_service.geocode(city, city) or amap_service.geocode(f"{city}市政府", city)
            if center:
                return center
        except Exception as exc:  # noqa: BLE001
            logger.warning("Resolve city center failed for %s: %s", city, exc)

        # 避免写死北京坐标: 使用城市名计算稳定兜底坐标（中国境内大致范围）
        seed = sum(ord(ch) for ch in city)
        longitude = 102.0 + (seed % 3000) / 100.0  # 102.00 - 131.99
        latitude = 22.0 + (seed % 1800) / 100.0  # 22.00 - 39.99
        return Location(longitude=longitude, latitude=latitude)

    def _build_offset_location(
        self, city_center: Location, day_idx: int, attraction_idx: int
    ) -> Location:
        offset_lng = ((day_idx + 1) * 0.012) + (attraction_idx * 0.006)
        offset_lat = ((day_idx + 1) * 0.008) + (attraction_idx * 0.004)
        return Location(
            longitude=city_center.longitude + offset_lng,
            latitude=city_center.latitude + offset_lat,
        )

    def _build_fallback_attractions_for_day(
        self,
        city: str,
        city_center: Location,
        day_idx: int,
        preferred_count: int,
        preferences: Optional[list[str]] = None,
    ) -> list[Attraction]:
        clean_prefs = [pref.strip() for pref in (preferences or []) if pref and pref.strip()]
        theme = clean_prefs[day_idx % len(clean_prefs)] if clean_prefs else "城市风貌"
        name_templates = [
            f"{city}{theme}文化街区",
            f"{city}城市地标观景点",
            f"{city}历史人文景区",
            f"{city}滨水休闲步道",
            f"{city}特色生活街区",
        ]
        attractions: list[Attraction] = []
        for idx in range(max(preferred_count, 0)):
            name = name_templates[(day_idx * 2 + idx) % len(name_templates)]
            attractions.append(
                Attraction(
                    name=name,
                    address=f"{city}市核心区域",
                    location=self._build_offset_location(city_center, day_idx, idx),
                    visit_duration=120,
                    description=f"围绕{city}{theme}主题安排，适合拍照与步行游览",
                    category="景点",
                )
            )
        return attractions


_multi_agent_planner: Optional[MultiAgentTripPlanner] = None
_planner_lock = threading.Lock()


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取多智能体旅行规划系统实例(线程安全单例)."""
    global _multi_agent_planner
    if _multi_agent_planner is None:
        with _planner_lock:
            if _multi_agent_planner is None:
                _multi_agent_planner = MultiAgentTripPlanner()
    return _multi_agent_planner

