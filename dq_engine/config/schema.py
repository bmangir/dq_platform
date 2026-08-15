from dataclasses import dataclass, field
from typing import Any

from dq_engine.core.models import Severity


@dataclass
class CheckConfig:
    name: str
    type: str
    severity: Severity
    parameters: dict
    anomaly: dict | None = None


@dataclass
class DQConfig:
    table: str
    checks: list[CheckConfig]


class ConfigValidator:

    def validate(self, config: dict) -> DQConfig:

        if not isinstance(config, dict):
            raise ValueError(
                "DQ configuration must be a dictionary."
            )

        table = config.get("table")

        if not table:
            raise ValueError(
                "Configuration must contain 'table'."
            )

        checks = config.get("checks")

        if not checks:
            raise ValueError(
                "Configuration must contain at least one check."
            )

        if not isinstance(checks, list):
            raise ValueError(
                "'checks' must be a list."
            )

        parsed_checks = [
            self._parse_check(check)
            for check in checks
        ]

        return DQConfig(
            table=table,
            checks=parsed_checks,
        )

    def _parse_check(self, check: dict) -> CheckConfig:

        if not isinstance(check, dict):
            raise ValueError(
                "Each check must be a dictionary."
            )

        name = check.get("name")
        rule_type = check.get("type")
        severity = check.get("severity")
        anomaly = check.get("anomaly"),

        if not name:
            raise ValueError(
                "Each check must contain 'name'."
            )

        if not rule_type:
            raise ValueError(
                f"Check '{name}' must contain 'type'."
            )

        if not severity:
            raise ValueError(
                f"Check '{name}' must contain 'severity'."
            )

        try:
            severity_enum = Severity(severity)
        except ValueError:
            raise ValueError(
                f"Invalid severity '{severity}' "
                f"for check '{name}'."
            )

        parameters = {
            key: value
            for key, value in check.items()
            if key not in {
                "name",
                "type",
                "severity",
            }
        }

        return CheckConfig(
            name=name,
            type=rule_type,
            severity=severity_enum,
            parameters=parameters,
            anomaly=anomaly,
        )