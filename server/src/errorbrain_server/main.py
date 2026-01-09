"""ErrorBrain Server - Verdict-focused API.

Architecture:
- spec/v1: The law for all data contracts
- core: Pure business logic (no HTTP, no frameworks)
- ports: Stable interfaces (IngestPort, QueryPort)
- api: Thin HTTP adapter (validates, maps, calls ports)
- storage: Port implementations (in-memory for now, DB later)

This module ties everything together.
"""

from __future__ import annotations

from errorbrain_server.api.app import app
from errorbrain_server.api.routes import analysis, explain, ingest
from errorbrain_server.ports import InMemoryStorage

# ============================================================
# Initialize storage (port implementations)
# ============================================================

storage = InMemoryStorage()

# ============================================================
# Wire ports into routes
# ============================================================

ingest.set_ingest_port(storage)
analysis.set_query_port(storage)
explain.set_query_port(storage)

# ============================================================
# Export the app
# ============================================================

__all__ = ["app"]
