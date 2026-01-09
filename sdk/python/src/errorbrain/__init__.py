"""ErrorBrain SDK - Send errors to your Second Brain."""

from errorbrain.client import (
    ErrorBrainClient,
    ErrorEvent,
    ExplainResponse,
    Verdict,
)

__version__ = "0.1.0"
__all__ = ["ErrorBrainClient", "ErrorEvent", "Verdict", "ExplainResponse"]
