from random import Random
from typing import Iterable, List


class ChaosBag:
    pass


class Difficulty:
    EASY = 0
    STANDARD = 1
    HARD = 2
    DIFFICULT = 3


class ChaosBag:
    _rnd = Random()

    def __init__(self, tokens: List[str]):
        self._tokens = tokens


class Scenario:
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def on_setting_up(self):
        pass

    def on_setup(self):
        pass


class Campaign:
    def __init__(self, name: str, scenarios: Iterable[Scenario]):
        self._name = name
        self._scenarios = scenarios

    @property
    def name(self) -> str:
        return self._name
