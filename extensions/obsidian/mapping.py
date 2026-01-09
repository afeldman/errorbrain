"""Mapping from spec/v1 Verdict to Obsidian template context.

This module transforms a spec-conformant Verdict into a context dictionary
suitable for Jinja2 template rendering.

No business logic or reasoning here – pure structural mapping.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SpecHypothesis(BaseModel):
    """Hypothesis from spec/v1/verdict."""

    title: str
    description: str
    confidence: float


class SpecImpact(BaseModel):
    """Impact from spec/v1/verdict."""

    severity: str
    affected_components: list[str]


class SpecRecommendedAction(BaseModel):
    """Recommended action from spec/v1/verdict."""

    title: str
    description: str
    urgency: str


class SpecVerdict(BaseModel):
    """Verdict from spec/v1 (minimal fields used by Obsidian extension)."""

    id: str
    event_id: str
    hypothesis: SpecHypothesis
    impact: SpecImpact
    recommended_actions: list[SpecRecommendedAction]
    evidence_refs: list[str]
    created_at: datetime


def verdict_to_template_context(verdict: SpecVerdict | dict) -> dict[str, Any]:
    """Convert a spec/v1 Verdict to a Jinja2 template context.

    This is the ONLY place where Obsidian structure meets spec/v1 fields.

    Args:
        verdict: Either a SpecVerdict model or a dict (parsed JSON).

    Returns:
        A dict suitable for rendering with Jinja2 templates.

    Example:
        >>> verdict_data = json.load(open('verdict.json'))
        >>> context = verdict_to_template_context(verdict_data)
        >>> rendered = template.render(**context)
    """
    # If dict, parse it as SpecVerdict to ensure spec compliance
    if isinstance(verdict, dict):
        verdict = SpecVerdict.model_validate(verdict)

    return {
        "verdict_id": verdict.id,
        "event_id": verdict.event_id,
        "hypothesis": {
            "title": verdict.hypothesis.title,
            "description": verdict.hypothesis.description,
            "confidence": verdict.hypothesis.confidence,
        },
        "impact": {
            "severity": verdict.impact.severity,
            "affected_components": verdict.impact.affected_components,
        },
        "recommended_actions": [
            {
                "title": action.title,
                "description": action.description,
                "urgency": action.urgency,
            }
            for action in verdict.recommended_actions
        ],
        "evidence_refs": verdict.evidence_refs,
        "created_at": verdict.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    }
