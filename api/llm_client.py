from __future__ import annotations

import os
from dataclasses import dataclass

from any_llm import AnyLLM  # offizieller Client


@dataclass
class LLMConfig:
    provider: str = os.getenv("ERRORBRAIN_PROVIDER", "openai")
    model: str = os.getenv("ERRORBRAIN_MODEL", "gpt-4.1-mini")
    api_key: str = os.getenv("ERRORBRAIN_API_KEY", "")


class ErrorBrainLLM:
    def __init__(self, config: LLMConfig | None = None) -> None:
        self.config = config or LLMConfig()
        self._client = AnyLLM.from_provider(
            self.config.provider,
            api_key=self.config.api_key,
        )

    async def explain_error(self, report: dict) -> str:
        prompt = self._build_prompt(report)

        # any-llm spricht im Prinzip das OpenAI-ChatCompletion-Format :contentReference[oaicite:2]{index=2}
        completion = await self._client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "Du bist ein Senior-Engineer & Debug-Experte."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )

        return completion.choices[0].message.content

    def _build_prompt(self, report: dict) -> str:
        tb = report.get("traceback") or "(kein Traceback übermittelt)"
        tags = ", ".join(report.get("tags") or [])
        meta = report.get("metadata") or {}

        return (
            "Analysiere den folgenden Fehler, erkläre verständlich, "
            "warum er auftritt, und gib konkrete nächste Schritte.\n\n"
            f"Sprache: {report.get('language')}\n"
            f"Projekt: {report.get('project')}\n"
            f"Tags: {tags}\n"
            f"Metadata: {meta}\n\n"
            f"Fehlermeldung:\n{report.get('message')}\n\n"
            f"Traceback:\n{tb}\n"
        )
