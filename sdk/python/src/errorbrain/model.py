# declaration.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import List

class Annotation(BaseModel):
    """
    Free-form key/value metadata attached to ErrorEvents.

    Examples:
        - stacktrace
        - severity
        - component
        - environment
        - git.commit
        - flux.kustomization
    """

    model_config = ConfigDict(extra="forbid")

    key: str
    value: str

class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str
    name: str
    version: str | None = None
    environment: str | None = None
    hostname: str | None = None
    tags: list[str] = Field(default_factory=list)

class RuntimeContext(BaseModel):
    language: str | None = None
    runtime: str | None = None
    environment: str | None = None


class LLMContext(BaseModel):
    provider: str | None = None
    model: str | None = None

class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    data: dict[str, Any]
    timestamp: str | None = None


class ErrorEvent(BaseModel):
    id: str

    model_config = ConfigDict(extra="forbid")
    timestamp: str
    source: Source
    message: str

    stack_trace: str | None = None
    error_type: str | None = None
    severity: str | None = None
    metadata: dict[str, Any] | None = None
    evidence: list[Evidence] | None = None

class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    confidence: float


class Impact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    severity: str
    affected_components: list[str]


class RecommendedAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str
    urgency: str

class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    event_id: str
    hypothesis: Hypothesis
    impact: Impact
    recommended_actions: list[RecommendedAction]
    evidence_refs: list[str]
    created_at: str


class ExplainResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    verdict_id: str
    summary: str
    details: str
    actions: list[str]
