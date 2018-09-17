from typing import Iterable


class Difficulty:
    EASY = 0
    STANDARD = 1
    HARD = 2
    DIFFICULT = 3


class Scenario:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name


class Campaign:
    def __init__(self, name: str, scenarios: Iterable[Scenario]):
        self._name = name
        self._scenarios = scenarios

    @property
    def name(self) -> str:
        return self._name
