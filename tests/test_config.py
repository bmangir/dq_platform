import pytest

from dq_engine.config.schema import (
    ConfigValidator,
)
from dq_engine.core.models import Severity


def test_valid_config():

    config = {
        "table": "public.orders",
        "checks": [
            {
                "name": "order_id_not_null",
                "type": "not_null",
                "column": "order_id",
                "severity": "critical",
            }
        ],
    }

    result = ConfigValidator().validate(config)

    assert result.table == "public.orders"

    assert len(result.checks) == 1

    check = result.checks[0]

    assert check.name == "order_id_not_null"
    assert check.type == "not_null"
    assert check.severity == Severity.CRITICAL
    assert check.parameters["column"] == "order_id"


def test_missing_table():

    config = {
        "checks": [
            {
                "name": "order_id_not_null",
                "type": "not_null",
                "column": "order_id",
                "severity": "critical",
            }
        ],
    }

    with pytest.raises(ValueError):
        ConfigValidator().validate(config)


def test_invalid_severity():

    config = {
        "table": "public.orders",
        "checks": [
            {
                "name": "order_id_not_null",
                "type": "not_null",
                "column": "order_id",
                "severity": "super_critical",
            }
        ],
    }

    with pytest.raises(ValueError):
        ConfigValidator().validate(config)