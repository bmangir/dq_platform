from dq_engine.core.result_store import ResultStore
from dq_engine.core.results import RunResult


class InMemoryResultStore(ResultStore):

    def __init__(self):
        self._results: list[RunResult] = []

    def save(self, run_result: RunResult) -> None:
        self._results.append(run_result)

    @property
    def results(self) -> list[RunResult]:
        return self._results