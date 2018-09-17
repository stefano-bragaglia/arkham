import sys
from random import Random
from typing import Iterable, List, Optional

rnd = Random()


class ChaosBag:
    def __init__(self, tokens: List[str]):
        self._tokens = tokens

    def reveal(self) -> str:
        return rnd.choice(self._tokens)


bag = ChaosBag([
    'elder', 'fail', 'skull', 'cultist', 'stone', 'monster',
    '+1', '+1', '+1', '0', '0', '0', '0', '-1', '-1', '-1', '-2'
])


class Character:
    def __init__(self, name: str, traits: List[str], combat: int, agility: int, health: int):
        self._name = name
        self._traits = traits
        self._combat = combat
        self._agility = agility
        self._health = health
        self._damage = 1
        self._location = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def traits(self) -> Iterable[str]:
        return self._traits

    @property
    def combat(self) -> int:
        return self._combat

    @property
    def agility(self) -> int:
        return self._agility

    @property
    def health(self) -> int:
        return self._health

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def location(self) -> Optional['Location']:
        return self._location

    def deal_damage(self, damage: int):
        OnDealingDamage.execute(self, damage)
        self._health -= min(damage, self._health)
        OnDamageDealt.execute(self)
        if self._health == 0:
            OnDefeated.execute(self)


class Enemy(Character):

    def __init__(self, name: str, traits: List[str], combat: int, agility: int, health: int, damage: int, horror: int):
        super().__init__(name, traits, combat, agility, health)
        self._damage = damage
        self._horror = horror

    @property
    def damage(self) -> int:
        return self._damage

    @property
    def horror(self) -> int:
        return self._horror


class Ally(Character):
    def __init__(self, name: str, occupation: str, traits: List[str], willpower: int, intellect: int, combat: int,
                 agility: int, health: int, sanity: int):
        super().__init__(name, traits, combat, agility, health)
        self._occupation = occupation
        self._willpower = willpower
        self._intellect = intellect
        self._sanity = sanity
        self._horror = 0

    @property
    def occupation(self) -> str:
        return self._occupation

    @property
    def willpower(self) -> int:
        return self._willpower

    @property
    def intellect(self) -> int:
        return self._intellect

    @property
    def health(self) -> int:
        return self._health

    @property
    def sanity(self) -> int:
        return self._sanity

    def deal_horror(self, horror: int = 0):
        OnDealingHorror.execute(self, horror)
        self._horror -= min(horror, self._sanity)
        OnHorrorDealt.execute(self)
        if self._horror == 0:
            OnDefeated.execute(self)


class Investigator(Ally):

    def __init__(self, name: str, occupation: str, traits: List[str], willpower: int, intellect: int, combat: int,
                 agility: int, health: int, sanity: int):
        super().__init__(name, occupation, traits, willpower, intellect, combat, agility, health, sanity)
        self._engaged = set()

    @property
    def engaged(self) -> Iterable[Enemy]:
        return self._engaged


class Game:
    pass


class OnEvent:
    pass


class Location:
    def __init__(self, name: str, shroud: int, clues: int, exits: List[str]):
        self._name = name
        self._shroud = shroud
        self._clues = clues
        self._exits = exits
        self._investigators = set()
        self._enemies = set()
        self._allies = set()

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
    def exits(self) -> Iterable[str]:
        return self._exits

    @property
    def allies(self) -> Iterable[Ally]:
        return self._allies

    @property
    def investigators(self) -> Iterable[Investigator]:
        return self._investigators

    @property
    def enemies(self) -> Iterable[Enemy]:
        return self._enemies


class OnLocationEvent(OnEvent):
    @staticmethod
    def execute(character: Character, location: Location):
        raise NotImplementedError


class OnEnterLocation(OnLocationEvent):
    @staticmethod
    def execute(character: Character, location: Location):
        print('%s enters the %s' % (character.name, location.name))


class OnLeaveLocation(OnLocationEvent):
    @staticmethod
    def execute(character: Character, location: Location):
        print('%s leaves the %s' % (character.name, location.name))


class OnSpawnLocation(OnLocationEvent):
    @staticmethod
    def execute(character: Character, location: Location):
        print('%s spawns in the %s' % (character.name, location.name))


class OnFight(OnEvent):
    @staticmethod
    def execute(attacker: Character, defender: Character):
        print('%s attacks the %s' % (attacker.name, defender.name))


class OnDealingDamage(OnEvent):
    @staticmethod
    def execute(character: Character, damage: int):
        print('The %s receives %s points of damage' % (character.name, damage))


class OnDamageDealt(OnEvent):
    @staticmethod
    def execute(character: Character):
        print('The %s now has a health of %s' % (character.name, character.health))


class OnDealingHorror(OnEvent):
    @staticmethod
    def execute(character: Character, horror: int):
        print('The %s receives %s points of horror' % (character.name, horror))


class OnHorrorDealt(OnEvent):
    @staticmethod
    def execute(character: Character):
        print('The %s now has a sanity of %s' % (character.name, character.sanity))


class OnDefeated(OnEvent):
    @staticmethod
    def execute(character: Character):
        print('The %s is defeated' % character.name)


class Action:
    def execute(self):
        raise NotImplementedError


class Fight(Action):
    def __init__(self, attacker: Character, defender: Character):
        self._attacker = attacker
        self._defender = defender

    @property
    def attacker(self) -> Character:
        return self._attacker

    @property
    def defender(self) -> Character:
        return self._defender

    # noinspection PyUnresolvedReferences
    def execute(self):
        OnFight.execute(self._attacker, self._defender)
        self._defender.deal_damage(self._attacker.damage)
        if type(self._attacker) is Enemy and type(self._defender) is Investigator:
            self._defender.deal_horror(self._attacker.horror)


class Spawn(Action):
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
        if type(self._character) == Ally:
            location = self._character.location
            if location:
                location._allies.remove(self._character)
            self._location._allies.add(self._character)

        elif type(self._character) == Investigator:
            location = self._character.location
            if location:
                location._investigators.remove(self._character)
            self._location._investigators.add(self._character)

        elif type(self._character) == Enemy:
            location = self._character.location
            if location:
                location._enemies.remove(self._character)
            self._location._enemies.add(self._character)

        else:
            raise ValueError('Unknown character type: %s' % type(self._character).__name__)


class Investigate(Action):
    def __init__(self, investigator: Investigator, location: Location):
        self._investigator = investigator
        self._location = location

    @property
    def investigator(self) -> Investigator:
        return self._investigator

    @property
    def location(self) -> Location:
        return self._location

    def execute(self):
        token = bag.reveal()
        if self.investigator.intellect >= self._location.shroud:
            pass


class Move(Action):
    def __init__(self, character: Character, location_from: Location, location_to: Location):
        self._character = character
        self._location_from = location_from
        self._location_to = location_to

    @property
    def character(self) -> Character:
        return self._character

    @property
    def location_from(self) -> Location:
        return self._location_from

    @property
    def location_to(self) -> Location:
        return self._location_to

    def execute(self):
        if not self._location_from.contains(self._character):
            raise ValueError('%s is not in the %s' % (self._character.name, self._location_from.name))

        if not self._location_from.connected(self._location_to):
            raise ValueError('The %s is not connected to the %s' % (self._location_from.name, self._location_to.name))

        self._location_from.leave(self._character)
        self._location_to.enter(self._character)


if __name__ == '__main__':
    i = Investigator('Roland Banks', 'The Fed', ['Agency', 'Detective'], 3, 3, 4, 2, 9, 5)
    s = Location('Study', 2, 2, [])

    h = Location('Hallway', 1, 0, ['Attic', 'Cellar', 'Parlor'])
    a = Location('Attic', 1, 2, ['Hallway'])
    c = Location('Cellar', 4, 2, ['Hallway'])
    p = Location('Parlor', 2, 0, ['Hallway'])

    gp = Enemy('Ghoul Priest', ['Humanoid', 'Monster', 'Ghoul', 'Elite'], 4, 4, 5, 2, 2)

    actions = [
        Spawn(i, s),
        Spawn(i, h),
        Spawn(gp, h),
        Move(i, h, a),
        Move(i, h, a),
        Move(i, a, c),
        Fight(i, gp),
        Fight(i, gp),
        Fight(i, gp),
        Fight(i, gp),
        Fight(i, gp),
    ]

    while actions:
        action = actions.pop(0)
        try:
            action.execute()
        except ValueError as e:
            print(str(e), file=sys.stderr)
        finally:
            print()
