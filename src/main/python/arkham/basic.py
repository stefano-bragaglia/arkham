from random import shuffle
from typing import List
from typing import Optional


class Card:
    def __init__(self, name: str):
        self.name = name


class InvestigatorCard(Card):
    pass


class Deck:
    def __init__(self, cards: List[Card] = None):
        self.cards = cards or []

    def draw(self) -> Optional[Card]:
        if not self.cards:
            return None

        return self.cards.pop()

    def insert(self, card: Card, index: int = None):
        if index is None:
            self.cards.append(card)
        else:
            self.cards.insert(index, card)

    def is_empty(self) -> bool:
        return not self.cards

    def shuffle(self):
        shuffle(self.cards)


class Phase:
    label = None

    def __init__(self, round: 'Round'):
        self.round = round

    def handle(self):
        print('Round #%d - %s Phase' % (self.round.counter, self.label))

    def advance(self) -> 'Phase':
        raise NotImplementedError


class SetupPhase(Phase):
    def handle(self):
        for investigator in self.round.investigators:
            investigator.deck.shuffle()
            print('%s shuffles the deck' % investigator.name)
            for i in range(0, 5):
                card = investigator.deck.draw()
                investigator.hand.insert(card)
                print('%s draws %s' % (investigator.name, card.name))
        self.round.advance()

    def advance(self) -> 'Phase':
        return InvestigatorPhase(self.round)


class MythosPhase(Phase):
    label = 'Mythos'

    def handle(self):
        self.round.counter += 1
        super().handle()
        self.round.advance()

    def advance(self) -> Phase:
        return InvestigatorPhase(self.round)


class InvestigatorPhase(Phase):
    label = 'Investigator'

    def handle(self):
        super().handle()

    def advance(self) -> Phase:
        return EnemyPhase(self.round)


class EnemyPhase(Phase):
    label = 'Enemy'

    def handle(self):
        super().handle()
        self.round.advance()

    def advance(self) -> Phase:
        return UpkeepPhase(self.round)


class UpkeepPhase(Phase):
    label = 'Upkeep'

    def handle(self):
        super().handle()
        self.round.advance()
        for investigator in self.round.investigators:
            investigator.resources += 1
            print('%s receives 1 resource for a total of %d' % (investigator.name, investigator.resources))
            if investigator.deck.is_empty():
                investigator.deck = investigator.pile
                investigator.pile = Deck()
                investigator.deck.shuffle()
                print('%s shuffles the discard pile into the deck' % investigator.name)
            card = investigator.deck.draw()
            investigator.hand.insert(card)
            print('%s draws %s' % (investigator.name, card.name))
            # if more than 8 discard

    def advance(self) -> Phase:
        return MythosPhase(self.round)


"""
The Upkeep Phase
Resolve these steps, in order:
1. Each investigator turns his mini card faceup.
2. Ready all exhausted cards. Each unengaged enemy that readies at the same location as an investigator engages at this 
   time.
3. Each investigator draws 1 card and gains 1 resource.
4. Each investigator with more than 8 cards in hand chooses and discards cards from his hand until only 8 cards remain.
After the above steps are complete, the round is over. Proceed to the Mythos phase of the next round.
"""


class Round:
    def __init__(self, investigators: List['Investigator']):
        self.investigators = investigators
        self.counter = 1
        self.phase = SetupPhase(self)
        self.phase.handle()

    def advance(self):
        self.phase = self.phase.advance()
        self.phase.handle()


class Location:
    def __init__(self, name: str, shroud: int, clues: int, exits: List[str]):
        self.name = name
        self.shroud = shroud
        self.clues = clues
        self.exits = exits or []
        self.locked = True
        self.description_1 = "You've been investigating the strange events occuring in Arkham for several days now. " \
                             "Your deck in covered in newspaper articles, police reports, and witness accounts."
        self.description_2 = "The door to your study has vanished."
        self.investigators = set()

    def unlock(self):
        if self.locked:
            print(self.description_2)
            self.locked = False


class Action:
    def __init__(self):
        pass


class Investigator:
    def __init__(self, name: str, deck: Deck):
        self.name = name
        self.deck = deck
        self.hand = Deck()
        self.pile = Deck()
        self.resources = 5
