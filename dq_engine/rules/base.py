from abc import ABC, abstractmethod
from typing import Any

from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import (
    ExecutionPlan,
    Severity,
)


class BaseRule(ABC):

    rule_type: str

    def __init__(
            self,
            name: str,
            severity: str | Severity,
            **config: Any,
    ):
        self.name = name
        self.severity = Severity(severity)
        self.config = config

    @abstractmethod
    def build(
            self,
            context: ExecutionContext,
    ) -> ExecutionPlan:
        pass