"""LLM-based Reasoning using the any-llm library.

This module provides an alternative reasoning strategy that leverages a
Large Language Model to generate hypotheses and recommended actions.
It is designed to be a drop-in replacement for the rules-based engine,
adhering to the same input/output contract.

This implementation is optional and is activated by setting the
`ERRORBRAIN_REASONING_MODE` environment variable to `llm`.
"""
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from any_llm import AnyLLM

from errorbrain_server.core.models import (
    ErrorEvent,
    Hypothesis,
    Impact,
    RecommendedAction,
    Verdict,
)


def analyze_with_llm(event: ErrorEvent) -> Verdict:
    """
    Generate a Verdict by interpreting the ErrorEvent with an LLM.

    This function uses the `any-llm` library to connect to a configured
    LLM provider (e.g., a local LM Studio instance). It constructs a
    prompt that instructs the LLM to act as a reasoning engine,
    generating a structured hypothesis and actionable recommendations.

    If the LLM fails or the output cannot be parsed, this function
    should raise an exception to allow the engine to fall back to the
    deterministic rules-based approach.

    Args:
        event: The normalized error event.

    Returns:
        A Verdict object generated from the LLM's analysis.
    """
    # 1. Setup any-llm client
    # client = AnyLLM() # Reads configuration from environment variables

    # 2. Construct a detailed prompt for the LLM
    # prompt = _build_llm_prompt(event)

    # 3. Query the LLM
    # response = client.chat.completions.create(
    #     model="some-model-name", # From ENV
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0.2,
    # )
    # llm_output = response.choices[0].message.content

    # 4. Parse the LLM output into a Verdict object.
    #    This is a critical step and requires robust parsing,
    #    potentially with a JSON output mode from the LLM.
    #    (For skeleton, we will return a placeholder)

    # Placeholder implementation:
    # In a real scenario, this would be derived from the LLM response.
    placeholder_hypothesis = Hypothesis(
        title=f"LLM-based analysis for: {event.source.name}",
        description=(
            "This is a placeholder hypothesis from the LLM. It would typically "
            "contain a summary of the likely root cause based on the event data."
        ),
        confidence=0.75,  # LLMs often provide a different confidence level
    )

    placeholder_impact = Impact(
        severity="warning",  # Placeholder
        affected_components=[event.source.name],
    )

    placeholder_actions = [
        RecommendedAction(
            title="Investigate based on LLM insight",
            description=(
                "The language model suggested a potential area of investigation. "
                "Review the full analysis and check system components."
            ),
            urgency="medium",
        )
    ]

    # This function is a skeleton and does not perform a real LLM call.
    # It returns a mock verdict to demonstrate the flow.
    verdict = Verdict(
        id=str(uuid4()),
        event_id=event.id,
        hypothesis=placeholder_hypothesis,
        impact=placeholder_impact,
        recommended_actions=placeholder_actions,
        evidence_refs=[],
        created_at=datetime.utcnow(),
    )

    # To complete this, one would need to add error handling and
    # the actual `any-llm` call and parsing logic.
    # For now, we raise a NotImplementedError to ensure it's not
    # used accidentally until fully implemented.
    raise NotImplementedError("LLM analysis is not fully implemented.")


def _build_llm_prompt(event: ErrorEvent) -> str:
    """Construct the prompt to send to the LLM."""
    # This is where the art of prompt engineering comes in.
    # The goal is to give the LLM clear instructions, context,
    # and a desired output format.
    prompt = f"""
Analyze the following error event and provide a verdict.

**Event Details:**
- Message: {event.message}
- Source: {event.source.name}
- Severity: {event.severity}
- Timestamp: {event.timestamp}
- Tags: {", ".join(event.source.tags or [])}
- Metadata: {event.metadata}
- Evidence Count: {len(event.evidence or [])}

**Instructions:**
1.  Generate a concise, one-sentence title for the hypothesis.
2.  Write a detailed, one-paragraph description of the most likely root cause.
3.  Provide a confidence score (0.0 to 1.0) for your hypothesis.
4.  Estimate the impact severity (info, warning, critical).
5.  List 2-3 concrete, actionable recommended actions with titles, descriptions, and urgency (low, medium, high).

**Output Format (Strict JSON):**
{{
  "hypothesis": {{
    "title": "...",
    "description": "...",
    "confidence": ...
  }},
  "impact": {{
    "severity": "..."
  }},
  "recommended_actions": [
    {{
      "title": "...",
      "description": "...",
      "urgency": "..."
    }}
  ]
}}
"""
    return prompt
