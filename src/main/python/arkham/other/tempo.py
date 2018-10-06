import re
from math import inf, log
from typing import Dict, List
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

Value = Union[bool, float, int, str]
Variable = str
Term = Union[Value, Variable]
Substitution = Dict[Variable, Term]

_var_pattern = re.compile(r'[_A-Z][_a-zA-Z0-9]*')


def is_variable(term: Term) -> bool:
    return isinstance(term, str) and _var_pattern.match(term)


def term_repr(term: Term) -> str:
    if any(isinstance(term, c) for c in [bool, float, int]):
        return str(term)

    if isinstance(term, str) and re.match(r'[_a-zA-Z][_a-zA-Z0-9]*', term):
        return str(term)

    return repr(term)


class Atom:
    def __init__(self, functor: str, terms: Tuple[Term, ...] = ()):
        self._functor = functor
        self._terms = terms

    def __hash__(self) -> int:
        value = hash(self._functor)
        for term in self._terms:
            value = value ** hash(term)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Atom):
            return False

        if term_repr(self._functor) != term_repr(other._functor):
            return False

        if len(self._terms) != len(other._terms):
            return False

        for i, term in enumerate(self._terms):
            if term_repr(term) != term_repr(other._terms[i]):
                return False

        return True

    def __repr__(self) -> str:
        if self._terms:
            return '%s(%s)' % (term_repr(self._functor), ', '.join(term_repr(t) for t in self._terms))

        return term_repr(self._functor)

    @property
    def functor(self) -> str:
        return self._functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._terms

    def get_arity(self) -> int:
        return len(self._terms)

    def is_ground(self) -> bool:
        return all(not is_variable(t) for t in self._terms)

    def unify(self, other: 'Atom') -> Optional[Substitution]:
        if not isinstance(other, Atom):
            return None

        if term_repr(self._functor) != term_repr(other._functor):
            return None

        if len(self._terms) != len(other._terms):
            return None

        substitution = {}
        for i, term in enumerate(self._terms):
            if is_variable(term):
                if term not in substitution:
                    substitution[term] = other._terms[i]
                elif substitution[term] != other._terms[i]:
                    return None

            elif term != other._terms[i]:
                return None

        return substitution

    def substitute(self, substitution: Substitution) -> 'Atom':
        return Atom(self.functor, tuple(substitution.get(t, t) if is_variable(t) else t for t in self._terms))


class Literal:
    def __init__(self, atom: Atom, negated: bool = False):
        self._negated = negated
        self._atom = atom

    def __hash__(self) -> int:
        return hash(self._negated) ** hash(self._atom)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Literal):
            return False

        if self._negated != other._negated:
            return False

        return self._atom == other._atom

    def __repr__(self) -> str:
        if self._negated:
            return '~%s' % self._atom

        return repr(self._atom)

    @property
    def negated(self) -> bool:
        return self._negated

    @property
    def functor(self) -> str:
        return self._atom.functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._atom.terms

    def get_arity(self) -> int:
        return self._atom.get_arity()

    def get_complement(self) -> 'Literal':
        return Literal(self._atom, not self._negated)

    def is_ground(self) -> bool:
        return self._atom.is_ground()

    def unify(self, other: 'Literal') -> Optional[Substitution]:
        if not isinstance(other, Literal):
            return None

        if self.negated != other.negated:
            return None

        return self._atom.unify(other._atom)

    def substitute(self, substitution: Substitution) -> 'Literal':
        return Literal(self._atom.substitute(substitution), self._negated)


class Clause:
    def __init__(self, head: Literal, body: Tuple[Literal, ...] = ()):
        self._head = head
        self._body = body

    def __hash__(self) -> int:
        value = hash(self._head)
        for literal in self._body:
            value = value ** hash(literal)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Clause):
            return False

        if self._head != other._head:
            return False

        if len(self._body) != len(other._body):
            return False

        for i, literal in enumerate(self._body):
            if literal != other._body[i]:
                return False

        return True

    def __repr__(self) -> str:
        if self._body:
            return '%s :- %s.' % (self._head, ', '.join(repr(l) for l in self._body))

        return '%s.' % self._head

    @property
    def head(self) -> Literal:
        return self._head

    @property
    def body(self) -> Iterable[Literal]:
        return self._body

    @property
    def literals(self) -> Iterable[Literal]:
        return [self._head, *self._body]

    def get_arity(self) -> int:
        return len(self._body)

    def is_fact(self) -> bool:
        return not self._body

    def is_ground(self) -> bool:
        return all(l.is_ground() for l in self.literals)

    def substitute(self, substitution: Substitution) -> 'Clause':
        return Clause(self._head.substitute(substitution), tuple(l.substitute(substitution) for l in self._body))


class Assignment:
    def __init__(self, substitution: Substitution, positive: bool):
        self._substitution = substitution
        self._positive = positive

    def __repr__(self) -> str:
        return '(%s) {%s}' % (
            ['-', '+'][self._positive],
            ', '.join('%s: %s' % (k, term_repr(v)) for k, v in sorted(self._substitution.items())),
        )

    @property
    def substitution(self) -> Substitution:
        return self._substitution

    @property
    def positive(self) -> bool:
        return self._positive

    def extend(self, literal: Literal, ground: List[Literal]) -> List['Assignment']:
        literal = literal.substitute(self._substitution)
        if not literal:
            return []

        table = {}
        for fact in ground:
            substitution = literal.unify(fact)
            if substitution:
                for variable, constant in substitution.items():
                    table.setdefault(variable, set()).add(constant)

        result = [self]
        for variable, constants in table.items():
            result = [Assignment({**s._substitution, variable: c}, self._positive) for c in constants for s in result]

        return result

    def satisfy(self, literal: Literal, ground: List[Literal]) -> bool:
        literal = literal.substitute(self._substitution)
        if not literal:
            return False

        return any(bool(literal.unify(fact)) for fact in ground)


class Example:
    def __init__(self, fact: Literal, positive: bool):
        if not fact.is_ground():
            raise ValueError('Examples should be ground: %s' % repr(fact))

        self._fact = fact
        self._positive = positive

    def __hash__(self) -> int:
        return hash(self._fact) * hash(self._positive)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._positive != other._positive:
            return False

        return self._fact == other._fact

    def __repr__(self) -> str:
        return '(%s) %s' % (['-', '+'][self._positive], repr(self._fact))

    @property
    def fact(self) -> Literal:
        return self._fact

    @property
    def positive(self) -> bool:
        return self._positive

    def get_assignment(self, target: Literal) -> Optional[Assignment]:
        substitution = target.unify(self._fact)
        if not substitution:
            return None

        return Assignment(substitution, self._positive)


class TrainingSet:
    def __init__(self, assignments: List[Assignment]):
        self._assignments = assignments

    def __repr__(self) -> str:
        return '\n'.join(repr(a) for a in self._assignments)

    @property
    def assignments(self) -> Iterable[Assignment]:
        return self._assignments

    def extend(self, literal: Literal, ground: List[Literal]) -> Tuple[int, List[Assignment]]:
        count, result = 0, []
        for assignment in self._assignments:
            if assignment.satisfy(literal, ground):
                count += 1
                for extension in assignment.extend(literal, ground):
                    if extension not in result:
                        result.append(extension)

        return count, result


class Program:
    def __init__(self, clauses: Tuple[Clause, ...]):
        self._clauses = clauses
        self._tabling = {}

    def __hash__(self) -> int:
        value = 1
        for clause in self._clauses:
            value = value ** hash(clause)

        return value

    def __eq__(self, other) -> bool:
        if not isinstance(other, Program):
            return False

        if len(self._clauses) != len(other._clauses):
            return False

        return all(c in other._clauses for c in self._clauses)

    def __repr__(self) -> str:
        return '\n'.join(repr(c) for c in self._clauses)

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._clauses

    def get_clause(self, index: int) -> Optional[Clause]:
        return self._clauses[index] if 0 <= index < len(self._clauses) else None

    def get_constants(self) -> List[Term]:
        return sorted({t for c in self._clauses for l in c.literals for t in l.terms if not is_variable(t)})

    def get_facts(self) -> Iterable[Clause]:
        return [f for f in self._clauses if f.is_fact()]

    def get_rules(self) -> Iterable[Clause]:
        return (fact for fact in self._clauses if not fact.is_fact())

    def is_ground(self) -> bool:
        return all(c.is_ground() for c in self._clauses)

    def resolve(self, query: Literal) -> Optional[List[Tuple[int, Literal, Substitution]]]:
        if not query.is_ground():
            raise ValueError("'query' must be ground: %s" % query)

        return self._tabling.setdefault(query, self._resolve(query))

    def _resolve(self, query: Literal) -> Optional[List[Tuple[int, Literal, Substitution]]]:
        for i, clause in enumerate(self._clauses):
            substitution = clause.head.unify(query)
            if substitution is None:
                continue

            derivation = [(i, query, substitution)]
            if not clause.body:
                return derivation

            for query in clause.body:
                substituted = query.substitute(substitution)
                sub_goal = self.resolve(substituted)
                if not sub_goal:
                    return None

                derivation = [*derivation, *sub_goal]

            return derivation

        return None

    def get_world(self) -> List[Literal]:
        table = {}
        clauses = []
        root = Root()
        for rule in self._clauses:
            if rule.is_fact():
                clauses.append(rule)
            else:
                beta = None
                for lit in rule.body:
                    name = repr(lit)
                    alpha = table.setdefault(name, Alpha(lit, root))
                    if beta is None:
                        beta = alpha
                    else:
                        name = '%s, %s' % (beta.name, alpha.name)
                        beta = table.setdefault(name, Beta(beta, alpha))
                Leaf(rule, beta, root, clauses)

        for fact in self.get_facts():
            root.notify(fact.head)

        return list({c.head for c in clauses})

    def foil(self, target: Literal, examples: List[Example]) -> List[Clause]:
        training_set = TrainingSet([e.get_assignment(target) for e in examples])

        ground = self.get_world()

        clauses = []
        while any(e.positive for e in training_set.assignments):
            clause = self.new_clause(target, training_set)
            if not clause:
                raise ValueError("Shouldn't have happened")

            clauses.append(clause)
            training_set = TrainingSet([a for a in training_set.assignments if not a.satisfy(target, ground)])

        return clauses

    def new_clause(self, target: Literal, training_set: TrainingSet) -> Clause:
        body, current_examples = [], training_set
        while any(not e.positive for e in current_examples):
            candidates = self.new_literals(target, body)
            literal, extended_examples = self.choose_literal(candidates, current_examples)
            if literal:
                body = (*body, literal)
                current_examples = extended_examples

        return Clause(target, body)

    def choose_literal(self, literals: List[Literal], training_set: TrainingSet) -> Tuple[Literal, List[Example]]:
        best, literal, extended_examples = None, None, training_set
        for literal in literals:
            max_gain = cover(extended_examples, literal) * information(extended_examples)
            if best is not None and max_gain < best:
                continue

            # future_examples = []
            # for example in extended_examples:
            #     for e in example.extend(literal, self.get_constants()):
            #         if e not in future_examples:
            #             future_examples.append(e)

            future_examples = [ee for e in extended_examples for ee in e.extend(literal, self.get_constants())]
            gain = cover(examples, literal) * (information(examples) - information(future_examples))
            if best is None or gain > best:
                best, literal, extended_examples = gain, literal, future_examples

        return literal, extended_examples

    def new_literals(self, head: Literal, body: List[Literal]) -> List[Literal]:
        literals = []
        count = self._count(head, body)
        for negated, functor, arity in self._get_signatures():
            for indexes in self._get_indexes(count, arity):
                literal = Literal(Atom(functor, tuple('V%d' % i for i in indexes)), negated)
                if literal not in literals:
                    literals.append(literal)

        return literals

    def extend(self, example: Example, literal: Literal) -> List[Example]:
        raise NotImplementedError

    # def extend(self, literal: Literal, ground: List[Literal]) -> Tuple[int, List[Assignment]]:
    #     count, result = 0, []
    #     for assignment in self._assignments:
    #         if assignment.satisfy(literal, ground):
    #             count += 1
    #             for extension in assignment.extend(literal, ground):
    #                 if extension not in result:
    #                     result.append(extension)
    #
    #     return count, result

    def _get_signatures(self) -> List[Tuple[bool, str, int]]:
        signatures = []
        for clause in self._clauses:
            signature = (clause.head.negated, clause.head.functor, clause.head.get_arity())
            if signature not in signatures:
                signatures.append(signature)

        return signatures

    @staticmethod
    def _count(head: Literal, body: List[Literal]) -> int:
        indexes = {}
        for literal in [*body, head]:
            for term in literal.terms:
                if is_variable(term):
                    indexes.setdefault(term, len(indexes))

        return len(indexes)

    @staticmethod
    def _get_indexes(count: int, arity: int) -> List[List[int]]:
        items = [[]]
        for _ in range(arity):
            updates = []
            for combination in items:
                for current in range(count + arity - 1):
                    update = [*combination, current]
                    updates.append(update)
            items = updates
        valid_items = [p for p in items if any(i < count for i in p)]

        return sorted(valid_items, key=lambda x: sum(1 for i in x if i < count))


Payload = Tuple[List[Literal], Substitution]


class Root:
    def __init__(self):
        self.children = set()

    def notify(self, ground: Literal):
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

    def notify(self, ground: Literal, substitution: Substitution, parent: Root):
        substitution = self.pattern.unify(ground)
        if substitution is not None:
            payload = ([ground], substitution)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify([ground], substitution, self)


Node = Union[Alpha, 'Beta']


class Beta:
    def __init__(self, parent_1: Node, parent_2: Alpha):
        self.parent_1 = parent_1
        self.parent_2 = parent_2
        self.name = '%s, %s' % (parent_1.name, parent_2.name)
        self.memory = []
        self.children = set()
        parent_1.children.add(self)
        parent_2.children.add(self)

    def notify(self, ground: List[Literal], substitution: Substitution, parent: Node):
        if parent is self.parent_1:
            for ground_2, subs_2 in self.parent_2.memory:
                self._notify(ground, substitution, ground_2, subs_2)
        elif parent is self.parent_2:
            for ground_1, subs_1 in self.parent_1.memory:
                self._notify(ground_1, subs_1, ground, substitution)

    @staticmethod
    def _unify(substitution_1: Substitution, substitution_2: Substitution) -> Optional[Substitution]:
        for var in set(substitution_1).intersection(substitution_2):
            if substitution_1[var] != substitution_2[var]:
                return None

        return {**substitution_1, **substitution_2}

    def _notify(self, ground_1: List[Literal], substitution_1: Substitution,
                ground_2: List['Literal'], substitution_2: Substitution):
        subs = self._unify(substitution_1, substitution_2)
        if subs is not None:
            ground = [*ground_1, *ground_2]
            payload = (ground, subs)
            if payload not in self.memory:
                self.memory.append(payload)
                for child in self.children:
                    child.notify(ground, subs, self)


class Leaf:
    def __init__(self, clause: Clause, parent: Node, root: Root, agenda: List[Clause]):
        self.parent = parent
        self.clause = clause
        self.name = repr(clause)
        self.memory = []

        self.root = root
        self.agenda = agenda
        parent.children.add(self)

    def notify(self, ground: List[Literal], substitution: Substitution, parent: Node):
        payload = (ground, substitution)
        if payload not in self.memory:
            self.memory.append(payload)

            literal = self.clause.head.substitute(substitution)
            clause = Clause(literal, (*ground,))
            if clause not in self.agenda:
                self.agenda.append(clause)

            self.root.notify(literal)


def cover(examples: List[Example], literal: Literal) -> int:
    return sum(1 for e in examples if e.is_covered(literal))


def max_gain(examples: List[Example], literal: Literal) -> float:
    return cover(examples, literal) * information(examples)


def information(examples: List[Example]) -> float:
    if not examples:
        return -inf

    pos = sum(1 for e in examples if e.positive)
    if pos == 0:
        return inf

    return -log(pos / len(examples))  # / log(2)


def parenthood():
    p = Program((
        Clause(Literal(Atom('father', ('frank', 'abe')))),
        Clause(Literal(Atom('father', ('frank', 'alan')))),
        Clause(Literal(Atom('father', ('alan', 'sean')))),
        Clause(Literal(Atom('father', ('sean', 'jane')))),
        Clause(Literal(Atom('father', ('george', 'bob')))),
        Clause(Literal(Atom('father', ('george', 'tim')))),
        Clause(Literal(Atom('father', ('bob', 'jan')))),
        Clause(Literal(Atom('father', ('tim', 'tom')))),
        Clause(Literal(Atom('father', ('tom', 'thomas')))),
        Clause(Literal(Atom('father', ('ian', 'ann')))),
        Clause(Literal(Atom('father', ('thomas', 'billy')))),
        Clause(Literal(Atom('mother', ('rebecca', 'alan')))),
        Clause(Literal(Atom('mother', ('rebecca', 'abe')))),
        Clause(Literal(Atom('mother', ('joan', 'sean')))),
        Clause(Literal(Atom('mother', ('jane', 'ann')))),
        Clause(Literal(Atom('mother', ('jannet', 'tim')))),
        Clause(Literal(Atom('mother', ('jannet', 'bob')))),
        Clause(Literal(Atom('mother', ('tammy', 'tom')))),
        Clause(Literal(Atom('mother', ('tipsy', 'thomas')))),
        Clause(Literal(Atom('mother', ('debrah', 'billy')))),
        Clause(Literal(Atom('mother', ('jill', 'jan')))),
        Clause(Literal(Atom('mother', ('jan', 'jane')))),
    ))
    print(p)
    print()


def connectedness():
    program = Program((
        Clause(Literal(Atom('edge', (0, 1)))),
        Clause(Literal(Atom('edge', (0, 3)))),
        Clause(Literal(Atom('edge', (1, 2)))),
        Clause(Literal(Atom('edge', (3, 2)))),
        Clause(Literal(Atom('edge', (3, 4)))),
        Clause(Literal(Atom('edge', (4, 5)))),
        Clause(Literal(Atom('edge', (4, 6)))),
        Clause(Literal(Atom('edge', (6, 8)))),
        Clause(Literal(Atom('edge', (7, 6)))),
        Clause(Literal(Atom('edge', (7, 8)))),
    ))
    print(program)
    print()

    examples = []
    for x in range(9):
        for y in range(9):
            fact = Literal(Atom('edge', (x, y)))
            positive = Clause(fact) in program.clauses
            examples.append(Example((fact,), positive))
    target = Literal(Atom('path', ('X', 'Y')))
    result = program.foil(examples, target)
    for clause in result:
        print(clause)

    #
    #
    # e = Example((Literal(Atom('edge', (0, 1))),), True)
    # print(e.extend(
    #     [Literal(Atom('edge', ('X', 'Z')))],
    #     Literal(Atom('path', ('Z', 'Y'))),
    #     [0, 1, 2, 3, 4, 5, 6, 7, 8]
    # ))


def abstract():
    program = Program((
        Clause(Literal(Atom('q', ('X', 'Y'))), (Literal(Atom('p', ('Y', 'X'))),)),
        Clause(Literal(Atom('p', (1, 2)))),
    ))
    print(program)
    print()
    query = Literal(Atom('q', (2, 1)))
    print('?-', query)
    derivation = program.resolve(query)
    if derivation:
        print('YES')
        for step in derivation:
            clause = program.get_clause(step[0])
            subs = '{%s}' % ', '.join('%s: %s' % (k, term_repr(v)) for k, v in step[2].items())
            print('    ', clause, '  /  ', subs, '  /  ', step[1])
    else:
        print('NO')

    # result = program.learn(Literal(Atom('q', ('V0', 'V1'))), [Literal(Atom('q', (2, 1)))], [])
    # for clause in result:
    #     print('\t', clause)


if __name__ == '__main__':
    # abstract()
    # connectedness()

    p = Program((
        Clause(Literal(Atom('edge', (0, 1)))),
        Clause(Literal(Atom('edge', (0, 3)))),
        Clause(Literal(Atom('edge', (1, 2)))),
        Clause(Literal(Atom('edge', (3, 2)))),
        Clause(Literal(Atom('edge', (3, 4)))),
        Clause(Literal(Atom('edge', (4, 5)))),
        Clause(Literal(Atom('edge', (4, 6)))),
        Clause(Literal(Atom('edge', (6, 8)))),
        Clause(Literal(Atom('edge', (7, 6)))),
        Clause(Literal(Atom('edge', (7, 8)))),
    ))

    tgt = Literal(Atom('path', ('X', 'Y')))
    lt1 = Literal(Atom('edge', ('X', 'Y')))
    lt2 = Literal(Atom('edge', ('X', 'Z')))

    cons = [i for i in range(9)]

    a1 = Assignment({'X': 0, 'Y': 1}, True)
    a2 = Assignment({'X': 0, 'Y': 7}, False)

    t1 = TrainingSet([a1, a2])

    print(t1)

    print(t1.extend(lt2, p.get_world()))
