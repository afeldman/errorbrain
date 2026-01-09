"""API module init."""

from errorbrain_server.api import routes
from errorbrain_server.api.app import app
from errorbrain_server.api.mapping import core_verdict_to_explain, core_verdict_to_spec, spec_event_to_core
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

__all__ = [
    "app",
    "routes",
    "spec_event_to_core",
    "core_verdict_to_spec",
    "core_verdict_to_explain",
    "SpecErrorEvent",
    "SpecVerdict",
    "SpecExplainResponse",
]
