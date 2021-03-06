import json
import os
from typing import Dict, List, Optional

from dataclasses import dataclass

INVESTIGATORS = {
  "Roland Banks": {
    "unique": True,
    "name": "Roland Banks",
    "occupation": "The Fed",
    "class_": "Guardian",
    "traits": [
      "Agency",
      "Detective"
    ],
    "willpower": 3,
    "intellect": 3,
    "combat": 4,
    "agility": 2,
    "health": 9,
    "sanity": 5,
    "abilities": [
      "<react> After you defeat an enemy: Discover 1 clue at your location. (Limit once per round.)",
      "<elder> effect: +1 for each clue on your location."
    ],
    "flavour": "Everything by the book: every \"i\" dotted, every \"t\" crossed. It has worked, until now.",
    "artist": "Magali Villeneuve",
    "pack": "Core Set",
    "number": 1,
    "deck": {
      "size": 30,
      "options": {
        "Guardian": {
          "min": 0,
          "max": 5
        },
        "Seeker": {
          "min": 0,
          "max": 2
        },
        "Neutral": {
          "min": 0,
          "max": 5
        }
      },
      "requirements": [
        "Roland's .38 Special",
        "Cover Up",
        "1 random basic weakness"
      ]
    },
    "bio": "Roland had always taken comfort in procedure and rules. As an agent in the Bureau, he was relieved to have guidelines to follow in any given situation. But lately, his Federal Agent's Handbook had been entirely unhelpful given the cases he'd been assigned. Try as he might, Roland could find no mention of what to do when confronted with strange creatures, gates through time and space, or magic spells. If he hadn't seen it with his own eyes, he would never have believed it... and there's no way his superiors would understand. Roland knew he would have to handle this one himself."
  },
  "Daisy Walker": {
    "unique": True,
    "name": "Daisy Walker",
    "occupation": "The Librarian",
    "class_": "Seeker",
    "traits": ["Miskatonic"],
    "willpower": 3,
    "intellect": 5,
    "combat": 2,
    "agility": 2,
    "health": 5,
    "sanity": 9,
    "abilities": [
      "You may take an additional action during your turn, which can only be used on Tome <action> abilities.",
      "<elder> effect: +0. If you succeed, draw 1 card for each Tome you control."
    ],
    "flavour": "I know of books so powerful, they can rewrite reality.",
    "artist": "Magali Villeneuve",
    "pack": "Core Set",
    "number": 2,
    "deck": {
      "size": 30,
      "options": {
        "Seeker": {
          "min": 0,
          "max": 5
        },
        "Mystic": {
          "min": 0,
          "max": 2
        },
        "Neutral": {
          "min": 0,
          "max": 5
        }
      },
      "requirements": [
        "Daisy’s Tote Bag", 
        "The Necronomicon (John Dee Translation)",
        "1 random basic weakness"
      ]
    },
    "bio": "As a respected librarian at Miskatonic University, Daisy had always felt that books were the most important thing in her life. She explored in fiction what she abhorred in life: horror, violence, fear. Then, she stumbled across the John Dee translation of the Necronomicon. It was blasphemous, unholy, and too awful to be read. But given her studies in obscure and occult subjects, Daisy knew there was more truth than fiction within the book's pages. She began to wonder what other secrets the restricted collection of the Orne Library held..."
  }
}


@dataclass
class Interval:
    min: int
    max: int


@dataclass
class Guideline:
    size: int
    options: Dict[str, Interval]
    requirements: List[str]


@dataclass
class Investigator:
    unique: bool
    name: str
    occupation: str
    class_: str
    traits: List[str]
    willpower: int
    intellect: int
    combat: int
    agility: int
    health: int
    sanity: int
    abilities: List[str]
    flavour: str
    artist: str
    pack: str
    number: str
    deck: Guideline
    bio: str


def load_json(filename: str) -> Dict:
    folder = os.path.dirname(__file__)
    fullname = os.path.join(folder, filename)
    with open(fullname, 'r') as file:
        return json.load(file)


class Game:
    def __init__(self):
        self.available_investigators = [Investigator(**values) for values in INVESTIGATORS.values()]
        self._investigators_completions = None

        self.investigators = []
        self.round = 1

    def get_investigators_completions(self) -> Dict[str, Investigator]:
        if self._investigators_completions is None:
            self._investigators_completions = {
                word.lower(): investigator
                for investigator in self.available_investigators
                for word in investigator.name.strip()
            }

        return self._investigators_completions

    def find_investigator(self, name: str) -> Optional[Investigator]:
        for investigator in self.available_investigators:
            if investigator.name == name:
                return investigator

        return None

    def add_investigator(self, investigator: Investigator) -> bool:
        if investigator not in self.investigators:
            self.investigators.append(investigator)
            return True

        return False

    def remove_investigator(self, investigator: Investigator) -> bool:
        if investigator in self.investigators:
            self.investigators.remove(investigator)
            return True

        return False
