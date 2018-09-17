import random
from cmd import Cmd
from typing import Optional

from arkham.game import Game


class State:
    label = None

    def __init__(self, game: Game):
        self.game = game

    def handle(self) -> Optional['State']:
        raise NotImplementedError


class Lobby(Cmd, State):
    intro = 'Welcome to Arkham Horror, the Card Game\n' \
            'Type \'help\' for more information, TAB for auto-completion.'
    prompt = '\n> '

    def __init__(self, game: Game, completekey='tab', stdin=None, stdout=None):
        super().__init__(completekey='tab', stdin=None, stdout=None)
        self.game = game
        self._next = None

    def handle(self) -> Optional['State']:
        self.cmdloop()

        return self._next

    def do_quit(self, arg):
        """Quit the program."""
        return True

    def do_start(self, arg):
        """Start the game."""
        self._next = Setup(self.game)

        return True

    def do_list(self, arg):
        """List the available investigators"""
        self._print_selected()
        self._print_available()

    def do_add(self, arg):
        """Add investigator to the game."""
        investigator = self.game.find_investigator(arg)
        if not investigator:
            print('Unknown investigator: %s' % arg)
        else:
            if self.game.add_investigator(investigator):
                print('%s has been added to the game.' % arg)
            else:
                print('%s is already in the game.')
            self._print_selected()

    def complete_add(self, text, line, start_index, end_index):
        completions = []
        print(self.game.get_investigators_completions())
        for word, investigator in self.game.get_investigators_completions().items():
            if investigator not in self.game.investigators:
                if not text or word.startswith(text.lower()):
                    if investigator.name not in completions:
                        completions.append(investigator.name)

        return completions

    def do_remove(self, arg):
        """Remove investigator from the game."""
        investigator = self.game.find_investigator(arg)
        if not investigator:
            print('Unknown investigator: %s' % arg)
        else:
            if self.game.remove_investigator(investigator):
                print('%s has been removed from the game.' % arg)
            else:
                print('%s is no more in the game.')
            self._print_selected()

    def complete_remove(self, text, line, start_index, end_index):
        completions = []
        for word, investigator in self.game.get_investigators_completions().items():
            if investigator in self.game.investigators:
                if not text or word.startswith(text.lower()):
                    if investigator.name not in completions:
                        completions.append(investigator.name)

        return completions

    def _print_selected(self):
        if not self.game.investigators:
            print('No investigator selected.')
        else:
            print('Selected investigators:')
            for investigator in self.game.investigators:
                print('*', investigator.name)

    def _print_available(self):
        available = [investigator for investigator in self.game.available_investigators
                     if investigator not in self.game.investigators]
        if not available:
            print('No investigator available.')
        else:
            print('Available investigators:')
            for investigator in available:
                print('*', investigator.name)


class Setup(State):
    def handle(self) -> Optional['State']:
        print('Setup')
        return InvestigatorPhase(self.game)


class MythosPhase(State):
    def handle(self) -> Optional['State']:
        print('Mythos Phase')
        if random.choice([False, True]):
            return Finish(self.game)

        return InvestigatorPhase(self.game)


class InvestigatorPhase(State):
    def handle(self) -> Optional['State']:
        print('Investigator Phase')
        if random.choice([False, True]):
            return Finish(self.game)

        return EnemyPhase(self.game)


class EnemyPhase(State):
    def handle(self) -> Optional['State']:
        print('Enemy Phase')
        if random.choice([False, True]):
            return Finish(self.game)

        return UpkeepPhase(self.game)


class UpkeepPhase(State):
    def handle(self) -> Optional['State']:
        print('Upkeep Phase')
        if random.choice([False, True]):
            return Finish(self.game)

        return MythosPhase(self.game)


class Finish(State):
    def handle(self) -> Optional['State']:
        print('Finish')
        return None


class Program:
    def __init__(self):
        self.state = Lobby(Game())

    def handle(self):
        while self.state:
            self.state = self.state.handle()
