"""Shared types for agents."""

from typing import Any

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Passed through the pipeline; extend as HelloAgents integration grows."""

    destination: str
    start_date_iso: str
    end_date_iso: str
    interests: list[str]
    party_size: int
    budget_hint: str | None = None
    extras: dict[str, Any] = Field(default_factory=dict)
