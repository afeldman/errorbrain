"""Mapping between spec models and core models.

This layer translates:
- Incoming spec/v1 JSON → core models
- Core models → outgoing spec/v1 JSON

It is the ONLY place where spec and core models interact.
"""

from __future__ import annotations

from errorbrain_server.api.spec_models import (
    SpecErrorEvent,
    SpecEvidence,
    SpecExplainResponse,
    SpecHypothesis,
    SpecImpact,
    SpecRecommendedAction,
    SpecSource,
    SpecVerdict,
)
from errorbrain_server.core import (
    ErrorEvent,
    Evidence,
    Hypothesis,
    Impact,
    RecommendedAction,
    Source,
    Verdict,
)


def spec_event_to_core(spec_event: SpecErrorEvent) -> ErrorEvent:
    """Convert incoming spec/v1 error event to core model."""
    source = Source(
        language=spec_event.source.language,
        name=spec_event.source.name,
        version=spec_event.source.version,
        environment=spec_event.source.environment,
        hostname=spec_event.source.hostname,
        tags=spec_event.source.tags if spec_event.source.tags else None,
    )

    evidence = None
    if spec_event.evidence:
        evidence = [
            Evidence(
                type=e.type,
                data=e.data,
                timestamp=e.timestamp,
            )
            for e in spec_event.evidence
        ]

    return ErrorEvent(
        id=spec_event.id,
        timestamp=spec_event.timestamp,
        source=source,
        message=spec_event.message,
        stack_trace=spec_event.stack_trace,
        error_type=spec_event.error_type,
        severity=spec_event.severity,
        metadata=spec_event.metadata,
        evidence=evidence,
    )


def core_verdict_to_spec(verdict: Verdict) -> SpecVerdict:
    """Convert core verdict to spec/v1 for output."""
    return SpecVerdict(
        id=verdict.id,
        event_id=verdict.event_id,
        hypothesis=SpecHypothesis(
            title=verdict.hypothesis.title,
            description=verdict.hypothesis.description,
            confidence=verdict.hypothesis.confidence,
        ),
        impact=SpecImpact(
            severity=verdict.impact.severity,
            affected_components=verdict.impact.affected_components,
        ),
        recommended_actions=[
            SpecRecommendedAction(
                title=a.title,
                description=a.description,
                urgency=a.urgency,
            )
            for a in verdict.recommended_actions
        ],
        evidence_refs=verdict.evidence_refs,
        created_at=verdict.created_at,
    )


def core_verdict_to_explain(verdict: Verdict) -> SpecExplainResponse:
    """Convert core verdict to human-readable explanation."""
    summary = (
        f"{verdict.hypothesis.title} (severity: {verdict.impact.severity}, "
        f"confidence {verdict.hypothesis.confidence:.2f})"
    )
    details = verdict.hypothesis.description
    actions = [
        f"[{a.urgency}] {a.title}: {a.description}" for a in verdict.recommended_actions
    ]

    return SpecExplainResponse(
        event_id=verdict.event_id,
        verdict_id=verdict.id,
        summary=summary,
        details=details,
        actions=actions,
    )
