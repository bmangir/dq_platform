import pytest

from dq_engine.config.loader import ConfigLoader
from dq_engine.config.schema import (
    ConfigValidator,
)
from dq_engine.core.models import Severity


def test_valid_config():

    config = {
        "table": {
            "name": "public.orders",
        },
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

    assert result.table.name == "public.orders"

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


def test_config_loads_anomaly_configuration():

    loader = ConfigLoader()

    config = loader.load(
        "configs/examples/orders_anomaly.yaml"
    )

    check = next(
        check
        for check in config.checks
        if check.name == "orders_row_count"
    )

    assert check.anomaly is not None

    assert check.anomaly["enabled"] is True

    assert (
            check.anomaly["method"]
            == "percentage_change"
    )

    assert (
            check.anomaly["threshold"]
            == 0.30
    )

    assert (
            check.anomaly["min_history"]
            == 1
    )