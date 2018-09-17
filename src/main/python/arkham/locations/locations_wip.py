from random import Random
from typing import Iterable, Optional, Set

import collections

rnd = Random()


class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]  # sentinel node for doubly linked list
        self.map = {}  # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


class Character:
    def __init__(self, name: str, willpower: int, intellect: int, combat: int, agility: int, health: int, sanity: int,
                 proper: bool):
        self._name = name
        self._willpower = willpower
        self._intellect = intellect
        self._combat = combat
        self._agility = agility
        self._health = health
        self._sanity = sanity
        self._damage = 0
        self._horror = 0
        self._clues = 0
        self._proper = proper
        self._location = None

    def __str__(self) -> str:
        if not self._proper:
            return 'the %s' % self._name

        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def willpower(self) -> int:
        return self._willpower

    @property
    def intellect(self) -> int:
        return self._intellect

    @property
    def combat(self) -> int:
        return self._combat

    @property
    def agility(self) -> int:
        return self._agility

    @property
    def health(self) -> int:
        return self._health - self._damage

    @property
    def sanity(self) -> int:
        return self._sanity - self._horror

    @property
    def clues(self) -> int:
        return self._clues

    @property
    def location(self) -> Optional['Location']:
        return self._location

    def enter(self, location: 'Location'):
        if self._location and location.name not in self._location.connected:
            raise ValueError(
                "%s can't go from %s to %s because they are not connected" % (self, self._location, location))

        if self._location:
            self._location.on_leaving(self)
            self._location._characters.remove(self)
            self._location.on_left(self)

        location.on_entering(self)
        location._characters.add(self)
        self._location = location
        location.on_entered(self)

    def investigate(self):
        if not self._location:
            raise ValueError(
                "%s must be in a location to investigate" % self)

        self.on_investigating()

        value = rnd.choice(range(-3, 2))

        self.on_investigated()

    def take_damage(self, amount: int):
        self._damage += min(amount, self._health - self._damage)
        print('%s takes %d damage/s and has %d left' % (self, amount, self.health))

    def take_horror(self, amount: int):
        self._horror += min(amount, self._sanity - self._horror)
        print('%s takes %d horror/s and has %d left' % (self, amount, self.sanity))


class Effect:
    @staticmethod
    def execute(character: Character):
        raise NotImplementedError


class Take1Damage(Effect):
    @staticmethod
    def execute(character: Character):
        character.take_damage(1)


class Take1Horror(Effect):
    @staticmethod
    def execute(character: Character):
        character.take_horror(1)


class Location:
    def __init__(self, name: str, shroud: int, clues: int, connected: Set[str], proper: bool = False,
                 on_entered: Effect = None):
        self._name = name
        self._proper = proper

        self._shroud = shroud
        self._clues = clues
        self._connected = sorted(connected)

        self._on_entered = on_entered

        self._revealed = False
        self._characters = OrderedSet()

    def __str__(self) -> str:
        if not self._proper:
            return 'the %s' % self._name

        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def shroud(self) -> int:
        return self._shroud

    @property
    def clues(self) -> int:
        return self._clues

    @property
    def connected(self) -> Iterable[str]:
        return self._connected

    @property
    def revealed(self) -> bool:
        return self._revealed

    @property
    def characters(self) -> Iterable[Character]:
        return self._characters

    def reveal(self):
        self.on_revealing()
        if not self._revealed:
            self._revealed = True
            self.on_revealed()

    def on_leaving(self, character: Character):
        pass
        # print('%s is leaving %s' % (character, self))

    def on_left(self, character: Character):
        print('%s has left %s' % (character, self))

    def on_entering(self, character: Character):
        pass
        # print('%s is entering %s' % (character, self))

    def on_entered(self, character: Character):
        print('%s has entered %s' % (character, self))
        self.reveal()
        if self._on_entered:
            self._on_entered.execute(character)

    def on_revealing(self):
        pass
        # print('%s is being revealed' % self)

    def on_revealed(self):
        print('%s has been revealed' % self)


class Action:
    def execute(self):
        raise NotImplementedError


class Investigate(Action):
    def __init__(self, character: Character):
        self._character = character

    @property
    def character(self) -> Character:
        return self._character

    def execute(self):
        try:
            self._character.investigate()
        except ValueError as e:
            print('> %s' % e)


class Move(Action):
    def __init__(self, character: Character, location: Location):
        self._character = character
        self._location = location

    @property
    def character(self) -> Character:
        return self._character

    @property
    def location(self) -> Location:
        return self._location

    def execute(self):
        try:
            self._character.enter(self._location)
        except ValueError as e:
            print('> %s' % e)


if __name__ == '__main__':
    study = Location('Study', 2, 2, set(), False)
    hallway = Location('Hallway', 1, 0, {'Attic', 'Cellar', 'Parlor'}, False)
    attic = Location('Attic', 1, 2, {'Hallway'}, False, Take1Horror())
    cellar = Location('Cellar', 4, 2, {'Hallway'}, False, Take1Damage())
    parlor = Location('Parlor', 4, 2, {'Hallway'}, False)

    banks = Character('Roland Banks', 3, 3, 4, 2, 9, 5, True)

    actions = [
        Move(banks, hallway),
        Move(banks, attic),
        Investigate(banks),
        Investigate(banks),
        Investigate(banks),
        Move(banks, cellar),
        Move(banks, hallway),
        Move(banks, cellar),
    ]

    while actions:
        action = actions.pop(0)
        action.execute()
