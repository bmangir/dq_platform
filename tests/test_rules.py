import pytest
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import Severity
from dq_engine.rules.completeness import (
    NotNullRule,
    RowCountRule,
)
from dq_engine.rules.uniqueness import UniqueRule
from dq_engine.rules.validity import AcceptedValuesRule, RangeRule


def test_not_null_rule_builds_execution_plan():

    rule = NotNullRule(
        name="order_id_not_null",
        severity=Severity.CRITICAL,
        column="order_id",
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == "order_id_not_null"
    assert plan.rule_type == "not_null"

    assert plan.severity == Severity.CRITICAL

    assert plan.operation == "count_nulls"

    assert plan.parameters == {
        "column": "order_id"
    }


def test_not_null_rule_requires_column():

    rule = NotNullRule(
        name="order_id_not_null",
        severity=Severity.CRITICAL,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="requires a 'column'",
    ):
        rule.build(context)


def test_row_count_rule_builds_execution_plan():

    rule = RowCountRule(
        name="orders_row_count",
        severity=Severity.CRITICAL,
        threshold={
            "min": 1,
            "max": 100000,
        },
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == "orders_row_count"
    assert plan.rule_type == "row_count"
    assert plan.severity == Severity.CRITICAL

    assert plan.operation == "row_count"

    assert plan.parameters == {
        "min": 1,
        "max": 100000,
    }


def test_row_count_rule_rejects_invalid_threshold():

    rule = RowCountRule(
        name="orders_row_count",
        severity=Severity.CRITICAL,
        threshold={
            "min": 100,
            "max": 10,
        },
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="min > max",
    ):
        rule.build(context)


def test_unique_rule_builds_execution_plan():

    rule = UniqueRule(
        name="order_id_unique",
        severity=Severity.HIGH,
        column="order_id",
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == "order_id_unique"
    assert plan.rule_type == "unique"
    assert plan.severity == Severity.HIGH

    assert plan.operation == "unique"

    assert plan.parameters == {
        "column": "order_id",
    }


def test_unique_rule_requires_column():

    rule = UniqueRule(
        name="order_id_unique",
        severity=Severity.HIGH,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="requires a 'column'",
    ):
        rule.build(context)

def test_accepted_values_rule_builds_execution_plan():

    rule = AcceptedValuesRule(
        name="order_status_valid",
        severity=Severity.HIGH,
        column="order_status",
        values=[
            "completed",
            "pending",
            "cancelled",
        ],
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == "order_status_valid"
    assert plan.rule_type == "accepted_values"
    assert plan.severity == Severity.HIGH

    assert plan.operation == "accepted_values"

    assert plan.parameters == {
        "column": "order_status",
        "values": [
            "completed",
            "pending",
            "cancelled",
        ],
    }


def test_accepted_values_requires_column():

    rule = AcceptedValuesRule(
        name="order_status_valid",
        severity=Severity.HIGH,
        values=[
            "completed",
            "pending",
        ],
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="requires a 'column'",
    ):
        rule.build(context)


def test_accepted_values_requires_values():

    rule = AcceptedValuesRule(
        name="order_status_valid",
        severity=Severity.HIGH,
        column="order_status",
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="requires at least one accepted value",
    ):
        rule.build(context)


def test_accepted_values_requires_list():

    rule = AcceptedValuesRule(
        name="order_status_valid",
        severity=Severity.HIGH,
        column="order_status",
        values="completed",
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="values.*list",
    ):
        rule.build(context)


def test_range_rule_builds_execution_plan():

    rule = RangeRule(
        name="order_amount_valid_range",
        severity=Severity.HIGH,
        column="order_amount",
        min=0,
        max=10000,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == (
        "order_amount_valid_range"
    )

    assert plan.rule_type == "range"
    assert plan.severity == Severity.HIGH

    assert plan.operation == "range"

    assert plan.parameters == {
        "column": "order_amount",
        "min": 0,
        "max": 10000,
    }


def test_range_rule_builds_execution_plan():

    rule = RangeRule(
        name="order_amount_valid_range",
        severity=Severity.HIGH,
        column="order_amount",
        min=0,
        max=10000,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.rule_name == (
        "order_amount_valid_range"
    )

    assert plan.rule_type == "range"
    assert plan.severity == Severity.HIGH

    assert plan.operation == "range"

    assert plan.parameters == {
        "column": "order_amount",
        "min": 0,
        "max": 10000,
    }


def test_range_rejects_invalid_bounds():

    rule = RangeRule(
        name="order_amount_valid_range",
        severity=Severity.HIGH,
        column="order_amount",
        min=100,
        max=10,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    with pytest.raises(
            ValueError,
            match="min.*greater than.*max",
    ):
        rule.build(context)


def test_range_allows_only_min():

    rule = RangeRule(
        name="order_amount_valid_range",
        severity=Severity.HIGH,
        column="order_amount",
        min=0,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.parameters["min"] == 0
    assert plan.parameters["max"] is None


def test_range_allows_only_min():

    rule = RangeRule(
        name="order_amount_valid_range",
        severity=Severity.HIGH,
        column="order_amount",
        min=0,
    )

    context = ExecutionContext(
        source=None,
        table="public.orders",
    )

    plan = rule.build(context)

    assert plan.parameters["min"] == 0
    assert plan.parameters["max"] is None