from dataclasses import dataclass
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"


@dataclass
class ExecutionPlan:
    rule_name: str
    rule_type: str

    operation: str
    parameters: dict[str, Any]


@dataclass
class CheckResult:
    rule_name: str
    rule_type: str

    status: CheckStatus
    severity: Severity

    total_rows: int | None = None
    failed_rows: int | None = None

    expected: Any = None
    actual: Any = None

    message: str | None = None
    execution_time_ms: float | None = None