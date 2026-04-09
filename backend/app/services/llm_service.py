"""LLM service wrapper with provider config support."""

from app.config import get_settings


class LLMService:
    def __init__(self) -> None:
        self._settings = get_settings()

    async def generate_trip_summary(self, destination: str, interests: list[str]) -> str:
        joined = ", ".join(interests) if interests else "城市经典路线"
        provider = self._settings.llm_provider.lower()
        model = self._settings.llm_model
        # TODO: integrate real provider SDK calls (OpenAI / DeepSeek compatible).
        return (
            f"[{provider}:{model}] 为 {destination} 生成的示例行程，重点关注：{joined}。"
        )
