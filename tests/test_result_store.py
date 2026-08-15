from dq_engine.core.models import (
    CheckResult,
    CheckStatus,
    Severity,
)
from dq_engine.core.results import RunResult
from dq_engine.core.run import RunContext
from dq_engine.storage.memory import InMemoryResultStore


def test_memory_result_store_saves_run_result():

    context = RunContext.create()

    check_result = CheckResult(
        rule_name="order_id_not_null",
        rule_type="not_null",
        status=CheckStatus.PASSED,
        severity=Severity.CRITICAL,
    )

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[check_result],
    )

    store = InMemoryResultStore()

    store.save(run_result)

    assert len(store.results) == 1
    assert store.results[0].run_id == run_result.run_id


def test_memory_result_store_can_save_multiple_runs():

    store = InMemoryResultStore()

    first_context = RunContext.create()
    second_context = RunContext.create()

    first_run = RunResult(
        run_id=first_context.run_id,
        started_at=first_context.started_at,
        finished_at=first_context.started_at,
        results=[],
    )

    second_run = RunResult(
        run_id=second_context.run_id,
        started_at=second_context.started_at,
        finished_at=second_context.started_at,
        results=[],
    )

    store.save(first_run)
    store.save(second_run)

    assert len(store.results) == 2
    assert store.results[0].run_id != store.results[1].run_id


def test_memory_result_store_get_run():

    store = InMemoryResultStore()

    context = RunContext.create()

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[],
    )

    store.save(run_result)

    found = store.get_run(
        run_result.run_id
    )

    assert found is not None
    assert found.run_id == run_result.run_id


def test_memory_result_store_returns_none_for_unknown_run():

    store = InMemoryResultStore()

    context = RunContext.create()

    assert (
            store.get_run(context.run_id)
            is None
    )


def test_memory_result_store_get_history():

    store = InMemoryResultStore()

    for _ in range(3):

        context = RunContext.create()

        check_result = CheckResult(
            rule_name="order_id_not_null",
            rule_type="not_null",
            status=CheckStatus.PASSED,
            severity=Severity.CRITICAL,
        )

        run_result = RunResult(
            run_id=context.run_id,
            started_at=context.started_at,
            finished_at=context.started_at,
            results=[check_result],
        )

        store.save(run_result)

    history = store.get_history(
        rule_name="order_id_not_null",
        limit=2,
    )

    assert len(history) == 2


def test_memory_result_store_history_filters_by_rule():

    store = InMemoryResultStore()

    context = RunContext.create()

    run_result = RunResult(
        run_id=context.run_id,
        started_at=context.started_at,
        finished_at=context.started_at,
        results=[
            CheckResult(
                rule_name="order_id_unique",
                rule_type="unique",
                status=CheckStatus.PASSED,
                severity=Severity.HIGH,
            )
        ],
    )

    store.save(run_result)

    history = store.get_history(
        rule_name="order_id_not_null",
    )

    assert history == []