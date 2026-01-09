"""Core reasoning engine for verdict generation - Deterministic Rules.

This module contains the deterministic rules and heuristics that
transform an ErrorEvent into a Verdict.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from errorbrain_server.core.models import (
    ErrorEvent,
    Hypothesis,
    Impact,
    RecommendedAction,
    Verdict,
)


def _map_severity(event_severity: str | None) -> str:
    """Map incoming severity level to verdict severity."""
    mapping = {
        "critical": "critical",
        "error": "critical",
        "warning": "warning",
        "info": "info",
        "debug": "info",
    }
    return mapping.get((event_severity or "").lower(), "info")


def _confidence_for(severity: str) -> float:
    """Derive confidence score from severity."""
    if severity == "critical":
        return 0.85
    if severity == "warning":
        return 0.7
    return 0.55


def _urgency_for(severity: str) -> str:
    """Map severity to recommended action urgency."""
    if severity == "critical":
        return "high"
    if severity == "warning":
        return "medium"
    return "low"


def _build_recommended_actions(event: ErrorEvent, severity: str) -> list[RecommendedAction]:
    """Generate recommended actions based on event and severity."""
    base_action = RecommendedAction(
        title="Inspect recent error",
        description=(
            "Review the error message and recent deployment or configuration changes. "
            "Use attached evidence where available."
        ),
        urgency=_urgency_for(severity),
    )

    actions: list[RecommendedAction] = [base_action]

    if severity == "critical":
        actions.append(
            RecommendedAction(
                title="Mitigate impact",
                description="Consider rolling back latest changes or scaling affected service while investigating.",
                urgency="high",
            )
        )

    if event.source.tags:
        actions.append(
            RecommendedAction(
                title="Check tagged context",
                description=f"Validate components tagged: {', '.join(event.source.tags)}",
                urgency=_urgency_for(severity),
            )
        )

    return actions


def _build_evidence_refs(event: ErrorEvent) -> list[str]:
    """Build evidence reference list from event."""
    if not event.evidence:
        return []
    return [f"{event.id}#e{idx}" for idx, _ in enumerate(event.evidence)]


def analyze_by_rules(event: ErrorEvent) -> Verdict:
    """Core reasoning: transform ErrorEvent into Verdict using deterministic rules.

    This is the heart of the deterministic rule-based system.

    Args:
        event: The normalized error event.

    Returns:
        A Verdict object ready for storage and serialization.
    """
    severity = _map_severity(event.severity)
    affected_components = [event.source.name]
    if event.metadata:
        component = event.metadata.get("component")
        if isinstance(component, str):
            affected_components.append(component)

    hypothesis = Hypothesis(
        title=f"Issue observed in {event.source.name}",
        description=event.message,
        confidence=_confidence_for(severity),
    )

    impact = Impact(
        severity=severity,
        affected_components=affected_components,
    )

    verdict = Verdict(
        id=str(uuid4()),
        event_id=event.id,
        hypothesis=hypothesis,
        impact=impact,
        recommended_actions=_build_recommended_actions(event, severity),
        evidence_refs=_build_evidence_refs(event),
        created_at=datetime.utcnow(),
    )

    return verdict
