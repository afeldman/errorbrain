"""Core Reasoning Orchestration Engine.

This module selects and orchestrates the reasoning process,
acting as the central entry point for verdict generation.

It can switch between different reasoning modes, such as deterministic
rules or LLM-based analysis.
"""
import os
from typing import Literal

from errorbrain_server.core.models import ErrorEvent, Verdict
from errorbrain_server.core.reasoning.rules import analyze_by_rules

# from .llm_anyllm import analyze_with_llm

ReasoningMode = Literal["rules", "llm"]


def get_reasoning_mode() -> ReasoningMode:
    """Determine the reasoning mode from environment variables."""
    mode = os.environ.get("ERRORBRAIN_REASONING_MODE", "rules").lower()
    if mode not in ("rules", "llm"):
        return "rules"
    return mode  # type: ignore


def analyze(event: ErrorEvent) -> Verdict:
    """
    Core reasoning entrypoint.

    Orchestrates the analysis of an ErrorEvent to produce a Verdict,
    switching between different reasoning modes based on configuration.

    Args:
        event: The normalized error event.

    Returns:
        A Verdict object.
    """
    mode = get_reasoning_mode()

    if mode == "llm":
        # Placeholder for LLM integration
        # try:
        #     return analyze_with_llm(event)
        # except Exception:
        #     # Fallback to rules if LLM fails
        #     return analyze_by_rules(event)
        return analyze_by_rules(event)  # Fallback for now

    return analyze_by_rules(event)
