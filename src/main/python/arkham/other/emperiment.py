from typing import List


class Status:
    pass


class Action:
    def __init__(self, name: str):
        self.name = name

    def is_apt(self, status: Status) -> bool:
        raise NotImplementedError

    def do(self, status: Status) -> Status:
        raise NotImplementedError


class Player:
    def __init__(self, name: str):
        self.name = name
        self.actions = set()

    def add_action(self, action: Action):
        self.actions.add(action)

    def remove_action(self, action: Action):
        self.actions.discard(action)


class Phase:
    def advance(self, input) -> 'Phase':
        raise NotImplementedError

    def run(self):
        raise NotImplementedError


class Game:
    def __init__(self, status: Status, players: List[Player], phase: Phase):
        self.players = players
        self.status = status
        self.phase = phase
        self._phase = None

    def is_over(self) -> bool:
        raise NotImplementedError

    def act(self):
        self._current = self.phase
        self._current.run()


class Lobby:
    def __init__(self):
        self.players = set()

    def add_player(self, player: Player):
        self.players.add(player)

    def remove_player(self, player: Player):
        self.players.discard(player)

    def get_game(self) -> Game:
        return Game(None, list(self.players))


if __name__ == '__main__':
    lobby = Lobby()
    lobby.add_player(Player('X'))
    lobby.add_player(Player('O'))

    game = lobby.get_game()

    while not game.is_over():
        game.act()
