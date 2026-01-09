"""Internal domain models for ErrorBrain Core.

These are NOT spec models and are owned by the business logic layer.
Spec models are in API mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Source:
    """Internal representation of error source."""

    language: str
    name: str
    version: str | None = None
    environment: str | None = None
    hostname: str | None = None
    tags: list[str] | None = None


@dataclass
class Evidence:
    """Internal representation of error evidence."""

    type: str
    data: dict[str, Any]
    timestamp: datetime | None = None


@dataclass
class ErrorEvent:
    """Internal representation of an error event.

    Used within core only; converted from/to spec models at boundaries.
    """

    id: str
    timestamp: datetime
    source: Source
    message: str
    stack_trace: str | None = None
    error_type: str | None = None
    severity: str | None = None
    metadata: dict[str, Any] | None = None
    evidence: list[Evidence] | None = None


@dataclass
class Hypothesis:
    """Internal reasoning result."""

    title: str
    description: str
    confidence: float


@dataclass
class Impact:
    """Internal impact assessment."""

    severity: str
    affected_components: list[str]


@dataclass
class RecommendedAction:
    """Internal action recommendation."""

    title: str
    description: str
    urgency: str


@dataclass
class Verdict:
    """Internal verdict (before serialization to spec).

    This is what the core produces. It will be mapped to spec/v1/verdict
    for output.
    """

    id: str
    event_id: str
    hypothesis: Hypothesis
    impact: Impact
    recommended_actions: list[RecommendedAction]
    evidence_refs: list[str]
    created_at: datetime
