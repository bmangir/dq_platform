from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext
from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)


def test_run_context_generates_run_id():

    context = RunContext.create()

    assert context.run_id is not None
    assert context.started_at is not None


def test_run_result_success():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.PASSED,
        severity=Severity.CRITICAL,
    )

    result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    assert result.success is True


def test_run_result_without_checks_is_not_successful():

    context = RunContext.create()

    result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[],
    )

    assert result.success is False


def test_run_result_is_not_successful_when_check_fails():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.FAILED,
        severity=Severity.CRITICAL,
    )

    result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    assert result.success is False


def test_run_result_is_not_successful_when_check_errors():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.ERROR,
        severity=Severity.CRITICAL,
    )

    result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    assert result.success is False