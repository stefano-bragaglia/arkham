from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

Payload = Tuple[List['Literal'], 'Substitution']


class Root:
    def __init__(self):
        self.children = set()

    def notify(self, ground: 'Literal'):
        for child in self.children:
            child.notify(ground, {}, self)


class Alpha:
    def __init__(self, pattern: 'Literal', parent: Root):
        self.parent = parent
        self.pattern = pattern
        self.name = repr(pattern)
        self.memory = []
        self.children = set()
        parent.children.add(self)

    def notify(self, ground: 'Literal', subs: 'Substitution', parent: Root):
        subs = self.pattern.unifies(ground)
        if subs is not None:
            payload = ([ground], subs)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify([ground], subs, self)


class Beta:
    def __init__(self, parent_1: Union[Alpha, 'Beta'], parent_2: Alpha):
        self.parent_1 = parent_1
        self.parent_2 = parent_2
        self.name = '%s, %s' % (parent_1.name, parent_2.name)
        self.memory = []
        self.children = set()
        parent_1.children.add(self)
        parent_2.children.add(self)

    def notify(self, ground: List['Literal'], subs: 'Substitution', parent: Union[Alpha, 'Beta']):
        if parent is self.parent_1:
            for ground_2, subs_2 in self.parent_2.memory:
                self._notify(ground, subs, ground_2, subs_2)
        elif parent is self.parent_2:
            for ground_1, subs_1 in self.parent_1.memory:
                self._notify(ground_1, subs_1, ground, subs)

    @staticmethod
    def _unifies(subs_1: 'Substitution', subs_2: 'Substitution') -> Optional['Substitution']:
        for var in set(subs_1).intersection(subs_2):
            if subs_1[var] != subs_2[var]:
                return None

        return {**subs_1, **subs_2}

    def _notify(self, ground_1: List['Literal'], subs_1: 'Substitution', ground_2: List['Literal'],
                subs_2: 'Substitution'):
        subs = self._unifies(subs_1, subs_2)
        if subs is not None:
            ground = [*ground_1, *ground_2]
            payload = (ground, subs)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify(ground, subs, self)


class Leaf:
    def __init__(self, rule: 'Rule', parent: Union[Alpha, Beta], root: Root, agenda: List):
        self.parent = parent
        self.rule = rule
        self.name = repr(rule)
        self.memory = []

        self.root = root
        self.agenda = agenda
        parent.children.add(self)

    def notify(self, ground: List['Literal'], subs: 'Substitution', parent: Union[Alpha, 'Beta']):
        from arkham.other.tempo import Clause

        payload = (ground, subs)
        if payload not in self.memory:
            self.memory.append(payload)

            lit = self.rule.head.substitutes(subs)
            # if self.rule.type is RuleType.STRICT:
            #     fact = Rule(lit, self.rule.type, [])
            #     if fact not in self.agenda:
            #         self.agenda.append(fact)

            rule = Clause(lit, ground)
            if rule not in self.agenda:
                self.agenda.append(rule)

            self.root.notify(lit)


def fire_rules(program: 'Program') -> List['Rule']:
    if program.is_ground():
        return program

    rules = []
    table = {}
    root = Root()
    for rule in program.rules:
        if rule.is_fact():
            rules.append(rule)
        else:
            beta = None
            for lit in rule.body:
                name = repr(lit)
                alfa = table.setdefault(name, Alpha(lit, root))
                if beta is None:
                    beta = alfa
                else:
                    name = '%s, %s' % (beta.name, alfa.name)
                    beta = table.setdefault(name, Beta(beta, alfa))
            Leaf(rule, beta, root, rules)

    for fact in program.get_facts():
        root.notify(fact.head)

    return rules
