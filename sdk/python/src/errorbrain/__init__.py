"""ErrorBrain SDK - Send errors to your Second Brain."""

from errorbrain.client import (
    ErrorBrainClient,
    ErrorEvent,
    ExplainResponse,
    Verdict,
)
from .annotations import ErrorAnnotation
from .decorators import errorbrain
from .context import llm_try

__version__ = "0.1.0"
__all__ = ["ErrorBrainClient",
    "ErrorEvent",
    "Verdict",
    "ExplainResponse",
    "ErrorAnnotation",
    "errorbrain",
    "llm_try",
]
