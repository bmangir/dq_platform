from dq_engine.core.metric_extractor import MetricExtractor
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext


def test_metric_extractor_extracts_numeric_metric():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.FAILED,
        severity=Severity.CRITICAL,
        total_rows=5,
        failed_rows=1,
        expected=0,
        actual=1,
        metric="null_count",
    )

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    extractor = MetricExtractor()

    metrics = extractor.extract(
        run_result
    )

    assert len(metrics) == 1

    metric = metrics[0]

    assert metric.run_id == run_result.run_id
    assert metric.rule_name == "order_id_not_null"
    assert metric.rule_type == "not_null"
    assert metric.metric_name == "null_count"
    assert metric.value == 1.0


def test_metric_extractor_ignores_result_without_metric():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="orders_schema",
        rule_type="schema",
        status=CheckStatus.PASSED,
        severity=Severity.HIGH,
        actual="valid",
    )

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    extractor = MetricExtractor()

    metrics = extractor.extract(
        run_result
    )

    assert metrics == []


def test_metric_extractor_extracts_multiple_metrics():

    context = RunContext.create()

    results = [
        CheckResult(
            rule_name="orders_row_count",
            rule_type="row_count",
            status=CheckStatus.PASSED,
            severity=Severity.HIGH,
            actual=500,
            metric="row_count",
        ),
        CheckResult(
            rule_name="order_id_not_null",
            rule_type="not_null",
            status=CheckStatus.PASSED,
            severity=Severity.CRITICAL,
            actual=0,
            metric="null_count",
        ),
        CheckResult(
            rule_name="order_id_unique",
            rule_type="unique",
            status=CheckStatus.FAILED,
            severity=Severity.HIGH,
            actual=3,
            metric="duplicate_count",
        ),
    ]

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=results,
    )

    extractor = MetricExtractor()

    metrics = extractor.extract(
        run_result
    )

    assert len(metrics) == 3

    assert metrics[0].metric_name == "row_count"
    assert metrics[0].value == 500.0

    assert metrics[1].metric_name == "null_count"
    assert metrics[1].value == 0.0

    assert metrics[2].metric_name == "duplicate_count"
    assert metrics[2].value == 3.0