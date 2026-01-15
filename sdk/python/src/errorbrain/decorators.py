from __future__ import annotations
from functools import wraps
from typing import Callable, Any, Optional

from .annotations import ErrorAnnotation
from .client import send_to_errorbrain


def errorbrain(
    *,
    component: Optional[str] = None,
    severity: Optional[str] = None,
    owner: Optional[str] = None,
    retryable: Optional[bool] = None,
    expected_errors: Optional[list[str]] = None,
    tags: Optional[list[str]] = None,
    project: Optional[str] = None,
):
    annotation = ErrorAnnotation(
        component=component,
        severity=severity,
        owner=owner,
        retryable=retryable,
        expected_errors=expected_errors,
        tags=tags or [],
    )

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                send_to_errorbrain(
                    exc,
                    project=project,
                    extra_context={
                        "annotation": annotation.to_context(),
                        "function": func.__qualname__,
                        "module": func.__module__,
                    },
                )
                raise

        return wrapper

    return decorator
