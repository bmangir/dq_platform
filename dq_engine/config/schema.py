from dataclasses import dataclass
from typing import Any

from dq_engine.core.models import Severity


@dataclass
class TableConfig:
    name: str


@dataclass
class CheckConfig:
    name: str
    type: str
    severity: Severity
    parameters: dict[str, Any]
    anomaly: dict[str, Any] | None = None


@dataclass
class DQConfig:
    table: TableConfig
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

        if not isinstance(table, dict):
            raise ValueError(
                "'table' must be a dictionary."
            )

        table_name = table.get("name")

        if not table_name:
            raise ValueError(
                "Table configuration must contain 'name'."
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
            table=TableConfig(
                name=table_name,
            ),
            checks=parsed_checks,
        )

    def _parse_check(
            self,
            check: dict,
    ) -> CheckConfig:

        if not isinstance(check, dict):
            raise ValueError(
                "Each check must be a dictionary."
            )

        name = check.get("name")
        rule_type = check.get("type")
        severity = check.get("severity")

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

        anomaly = check.get("anomaly")

        parameters = {
            key: value
            for key, value in check.items()
            if key not in {
                "name",
                "type",
                "severity",
                "anomaly",
            }
        }

        return CheckConfig(
            name=name,
            type=rule_type,
            severity=severity_enum,
            parameters=parameters,
            anomaly=anomaly,
        )