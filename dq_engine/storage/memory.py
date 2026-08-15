from uuid import UUID

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

    def get_run(
            self,
            run_id: UUID,
    ) -> RunResult | None:

        for result in self._results:
            if result.run_id == run_id:
                return result

        return None

    def get_history(
            self,
            rule_name: str,
            limit: int = 30,
    ) -> list[RunResult]:

        matched = []

        for run_result in reversed(self._results):

            if any(
                    result.rule_name == rule_name
                    for result in run_result.results
            ):
                matched.append(run_result)

            if len(matched) >= limit:
                break

        return matched