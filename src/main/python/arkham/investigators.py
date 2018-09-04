from enum import Enum
from typing import Dict


class InvestigatorClass(Enum):
    NEUTRAL = 0
    GUARDIAN = 1
    SEEKER = 2
    ROGUE = 3
    MYSTIC = 4
    SURVIVOR = 5


class Investigator:
    def __init__(self, name: str, role: str = None, class_: InvestigatorClass = InvestigatorClass.NEUTRAL):
        self.name = name
        self.role = role
        self.class_ = class_

    @property
    def title(self) -> str:
        if self.role:
            return '%s: %s' % (self.name, self.role)

        return self.name

    def __str__(self) -> str:
        return '%s (%s)' % (self.title, self.class_.name.title())


class InvestigatorPool:
    stop_words = ['a', 'an', 'the']

    def __init__(self):
        self.investigators = {
            Investigator('Roland Banks', 'The Fed', InvestigatorClass.GUARDIAN),
            Investigator('Daisy Walker', 'The Librarian', InvestigatorClass.SEEKER),
            Investigator('"Skids" O\'Toole', 'The Ex-Con', InvestigatorClass.ROGUE),
            Investigator('Agnes Baker', 'The Waitress', InvestigatorClass.MYSTIC),
            Investigator('Wendy Adams', 'The Urchin', InvestigatorClass.SURVIVOR),
        }
        self._completion = None

    def get_completion(self) -> Dict[str, Investigator]:
        if self._completion is None:
            self._completion = {}
            for investigator in self.investigators:
                words = {word.lower() for word in investigator.name.split()}
                if not investigator.role:
                    continue

                for word in investigator.role.split():
                    word = word.lower()
                    if word in self.stop_words:
                        continue

                    words.add(word)
                    for ch in ['"', "'"]:
                        if word.startswith(ch) and word.endswith(ch):
                            form = word[1:-1].strip()
                            if form:
                                words.add(form)

                for word in words:
                    if word in self._completion and self._completion[word] != investigator:
                        raise ValueError('Completion is inconsistent!')

                    self._completion[word] = investigator

        return self._completion


pool = InvestigatorPool()
