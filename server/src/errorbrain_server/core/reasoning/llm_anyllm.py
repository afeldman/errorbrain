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


import requests
import json
from errorbrain_server.core.models import (
    ErrorEvent,
    Hypothesis,
    Impact,
    RecommendedAction,
    Verdict,
)
from .config import LLM_ENABLED, LLM_KEY, LLM_HOST, LLM_MODEL

def _call_any_llm(prompt: str) -> dict:
    """Sendet einen OpenAI-kompatiblen Chat-Request an any-llm und gibt das JSON zurück."""
    url = LLM_HOST.rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {LLM_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 1024
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Extrahiere den Content
        content = data["choices"][0]["message"]["content"]
        # Versuche, JSON zu parsen
        return json.loads(content)
    except Exception as exc:
        raise RuntimeError(f"LLM-Request/Parsing fehlgeschlagen: {exc}")


def analyze_with_llm(event: ErrorEvent) -> Verdict:
    """
    Interpretiert das ErrorEvent mit einem LLM (any-llm) und liefert einen Verdict.
    Bei Fehlern wird eine Exception geworfen, damit der Engine-Fallback auf rules.py greift.
    """
    if not LLM_ENABLED:
        raise RuntimeError("LLMReasoner instantiated while LLM is disabled")
    prompt = _build_llm_prompt(event)
    try:
        llm_json = _call_any_llm(prompt)
        # Robust: Fallback auf Default-Werte, falls Felder fehlen
        hypothesis = Hypothesis(
            title=llm_json.get("hypothesis", {}).get("title", "LLM Hypothesis"),
            description=llm_json.get("hypothesis", {}).get("description", "No description."),
            confidence=llm_json.get("hypothesis", {}).get("confidence", 0.5),
        )
        impact = Impact(
            severity=llm_json.get("impact", {}).get("severity", "info"),
            affected_components=[event.source.name],
        )
        actions = []
        for act in llm_json.get("recommended_actions", []):
            actions.append(RecommendedAction(
                title=act.get("title", "LLM Action"),
                description=act.get("description", "No description."),
                urgency=act.get("urgency", "medium"),
            ))
        verdict = Verdict(
            id=str(uuid4()),
            event_id=event.id,
            hypothesis=hypothesis,
            impact=impact,
            recommended_actions=actions,
            evidence_refs=[],
            created_at=datetime.utcnow(),
        )
        return verdict
    except Exception as exc:
        # Fehler werden nach oben gereicht, Engine übernimmt Fallback
        raise RuntimeError(f"LLM-Analyse fehlgeschlagen: {exc}")


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
