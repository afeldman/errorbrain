from __future__ import annotations
from typing import Optional

from .annotations import ErrorAnnotation
from .client import send_to_errorbrain


class llm_try:
    def __init__(
        self,
        *,
        project: Optional[str] = None,
        component: Optional[str] = None,
        severity: Optional[str] = None,
        retryable: Optional[bool] = None,
        expected_errors: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ):
        self.project = project
        self.annotation = ErrorAnnotation(
            component=component,
            severity=severity,
            retryable=retryable,
            expected_errors=expected_errors,
            tags=tags or [],
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc is None:
            return False

        send_to_errorbrain(
            exc,
            project=self.project,
            extra_context={
                "annotation": self.annotation.to_context(),
                "context": "with llm_try",
            },
        )
        return False
