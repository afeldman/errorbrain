"""API Spec Models: Pydantic models aligned to spec/v1.

These are OUTPUT models (for serialization) and INPUT models (for validation).
They map to and from core models in the mapping layer.

They must be in sync with spec/v1 schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SpecSource(BaseModel):
    """Source model from spec/v1/error_event."""

    model_config = ConfigDict(extra="forbid")

    language: str
    name: str
    version: str | None = None
    environment: str | None = None
    hostname: str | None = None
    tags: list[str] = Field(default_factory=list)


class SpecEvidence(BaseModel):
    """Evidence model from spec/v1/error_event."""

    model_config = ConfigDict(extra="forbid")

    type: str
    data: dict[str, Any]
    timestamp: datetime | None = None


class SpecErrorEvent(BaseModel):
    """Input model for /events endpoint.

    Matches spec/v1/error_event.schema.json.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    timestamp: datetime
    source: SpecSource
    message: str
    stack_trace: str | None = None
    error_type: str | None = None
    severity: str | None = None
    metadata: dict[str, Any] | None = None
    evidence: list[SpecEvidence] | None = None

    @field_validator("id")
    @classmethod
    def validate_uuid(cls, value: str) -> str:
        try:
            UUID(value)
        except Exception as exc:
            raise ValueError("id must be a valid UUID string") from exc
        return value


class SpecHypothesis(BaseModel):
    """Hypothesis from spec/v1/verdict."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    confidence: float


class SpecImpact(BaseModel):
    """Impact from spec/v1/verdict."""

    model_config = ConfigDict(extra="forbid")

    severity: str
    affected_components: list[str]


class SpecRecommendedAction(BaseModel):
    """Recommended action from spec/v1/verdict."""

    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    urgency: str


class SpecVerdict(BaseModel):
    """Output model for verdict.

    Matches spec/v1/verdict.schema.json.
    """

    model_config = ConfigDict(extra="forbid")

    id: str
    event_id: str
    hypothesis: SpecHypothesis
    impact: SpecImpact
    recommended_actions: list[SpecRecommendedAction]
    evidence_refs: list[str]
    created_at: datetime


class SpecExplainResponse(BaseModel):
    """Output model for /explain endpoint."""

    model_config = ConfigDict(extra="forbid")

    event_id: str
    verdict_id: str
    summary: str
    details: str
    actions: list[str]
