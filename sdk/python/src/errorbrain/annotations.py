from __future__ import annotations
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ErrorAnnotation:
    component: Optional[str] = None
    severity: Optional[str] = None
    owner: Optional[str] = None
    retryable: Optional[bool] = None
    expected_errors: Optional[list[str]] = None
    tags: list[str] = field(default_factory=list)

    def to_context(self) -> Dict[str, Any]:
        return {
            k: v for k, v in {
                "component": self.component,
                "severity": self.severity,
                "owner": self.owner,
                "retryable": self.retryable,
                "expected_errors": self.expected_errors,
                "tags": self.tags,
            }.items() if v is not None
        }
