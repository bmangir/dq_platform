from abc import ABC, abstractmethod

from dq_engine.core.results import RunResult


class ResultStore(ABC):

    @abstractmethod
    def save(self, run_result: RunResult) -> None:
        pass