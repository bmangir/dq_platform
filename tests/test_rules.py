import pytest
from dq_engine.core.context import ExecutionContext
from dq_engine.core.models import Severity
from dq_engine.rules.completeness import NotNullRule


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