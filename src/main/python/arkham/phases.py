import random
from typing import Optional

from arkham.game import Game


class State:
    label = None

    def __init__(self, program: 'Program'):
        self.program = program

    def handle(self) -> Optional['State']:
        raise NotImplementedError


class Lobby(State):
    def handle(self) -> Optional['State']:
        print('Lobby')
        return Setup(self.program)


class Setup(State):
    def handle(self) -> Optional['State']:
        print('Setup')
        return InvestigatorPhase(self.program)


class MythosPhase(State):
    def handle(self) -> Optional['State']:
        print('Mythos Phase')
        if random.choice([False, True]):
            return Finish(self.program)

        return InvestigatorPhase(self.program)


class InvestigatorPhase(State):
    def handle(self) -> Optional['State']:
        print('Investigator Phase')
        if random.choice([False, True]):
            return Finish(self.program)

        return EnemyPhase(self.program)


class EnemyPhase(State):
    def handle(self) -> Optional['State']:
        print('Enemy Phase')
        if random.choice([False, True]):
            return Finish(self.program)

        return UpkeepPhase(self.program)


class UpkeepPhase(State):
    def handle(self) -> Optional['State']:
        print('Upkeep Phase')
        if random.choice([False, True]):
            return Finish(self.program)

        return MythosPhase(self.program)


class Finish(State):
    def handle(self) -> Optional['State']:
        print('Finish')
        return None


class Program:
    def __init__(self):
        self.game = Game()
        self.state = Lobby(self)

    def handle(self):
        while self.state:
            self.state = self.state.handle()
