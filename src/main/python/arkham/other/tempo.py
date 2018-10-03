import re
from math import inf, log
from pprint import pprint
from typing import Dict, List
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

Value = Union[bool, float, int, str]
Variable = str
Term = Union[Value, Variable]
Substitutions = Dict[Variable, Term]

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

    def unify(self, other: 'Atom') -> Optional[Substitutions]:
        if not isinstance(other, Atom):
            return None

        if term_repr(self._functor) != term_repr(other._functor):
            return None

        if len(self._terms) != len(other._terms):
            return None

        substitutions = {}
        for i, term in enumerate(self._terms):
            if is_variable(term):
                if term not in substitutions:
                    substitutions[term] = other._terms[i]
                elif substitutions[term] != other._terms[i]:
                    return None

            elif term != other._terms[i]:
                return None

        return substitutions

    def substitute(self, substitutions: Substitutions) -> 'Atom':
        return Atom(self.functor, tuple(substitutions.get(t, '_') if is_variable(t) else t for t in self._terms))


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

    def unify(self, other: 'Literal') -> Optional[Substitutions]:
        if not isinstance(other, Literal):
            return None

        if self.negated != other.negated:
            return None

        return self._atom.unify(other._atom)

    def substitute(self, substitutions: Substitutions) -> 'Literal':
        return Literal(self._atom.substitute(substitutions), self._negated)


class Example:
    def __init__(self, literal: Literal, negative: bool):
        if not literal or not literal.is_ground():
            raise ValueError('Examples must be ground: %s' % repr(literal))

        self._literal = literal
        self._negative = negative

    @property
    def negative(self) -> bool:
        return self._negative

    @property
    def negated(self) -> bool:
        return self._literal.negated

    @property
    def functor(self) -> str:
        return self._literal.functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._literal.terms

    def __hash__(self) -> int:
        return hash(self._literal) ** hash(self._negative)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Example):
            return False

        if self._negative != other._negative:
            return False

        return self._literal == other._literal

    def __repr__(self) -> str:
        return '#%s%s' % ('not ' if self._negative else '', repr(self._literal))

    def get_arity(self) -> int:
        return self._literal.get_arity()

    def is_ground(self) -> bool:
        return self._literal.is_ground()


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

    def substitute(self, substitutions: Substitutions) -> 'Clause':
        return Clause(self._head.substitute(substitutions), tuple(l.substitute(substitutions) for l in self._body))


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

    def get_constants(self) -> Iterable[Term]:
        return sorted({t for c in self._clauses for l in c.literals for t in l.terms if not is_variable(t)})

    def get_facts(self) -> Iterable[Clause]:
        return [f for f in self._clauses if f.is_fact()]

    def get_rules(self) -> Iterable[Clause]:
        return (fact for fact in self._clauses if not fact.is_fact())

    def is_ground(self) -> bool:
        return all(c.is_ground() for c in self._clauses)

    def resolve(self, query: Literal) -> Optional[List[Tuple[int, Literal, Substitutions]]]:
        if not query.is_ground():
            raise ValueError("'query' must be ground: %s" % query)

        return self._tabling.setdefault(query, self._resolve(query))

    def _resolve(self, query: Literal) -> Optional[List[Tuple[int, Literal, Substitutions]]]:
        for i, clause in enumerate(self._clauses):
            substitutions = clause.head.unify(query)
            if substitutions is None:
                continue

            derivation = [(i, query, substitutions)]
            if not clause.body:
                return derivation

            for query in clause.body:
                substituted = query.substitute(substitutions)
                sub_goal = self.resolve(substituted)
                if not sub_goal:
                    return None

                derivation = [*derivation, *sub_goal]

            return derivation

        return None

    def foil(self, examples: List[Example], target: Literal) -> List[Clause]:
        clauses = []

        while any(e.negated == False for e in examples):
            clause = self.new_clause(examples, target)
            clauses.append(clause)
            program = Program((*self._clauses, *clauses))
            examples = [e for e in examples if not program.resolve(e)]

        return clauses

    def new_clause(self, examples: List[Example], target: Literal) -> Clause:
        body = []

        extended_examples = [*examples]
        while any(e.negated for e in extended_examples):
            literal = self.choose_literal(self.new_literals(target, body), extended_examples)
            body = (*body, literal)
            extended_examples = [ee for e in extended_examples for ee in self.extend_example(e, literal)]

        return Clause(target, body)

    def choose_literal(self, literals: List[Literal], examples: List[Example]) -> Literal:
        for literal in literals:
            pass

    def new_literals(self, head: Literal, body: List[Literal]) -> List[Literal]:
        literals = []
        count = self._count(head, body)
        for negated, functor, arity in self._get_signatures():
            for indexes in self._get_indexes(count, arity):
                literal = Literal(Atom(functor, tuple('V%d' % i for i in indexes)), negated)
                if literal not in literals:
                    literals.append(literal)

        return literals

    def extend_example(self, example: Example, literal: Literal) -> List[Example]:
        pass

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
        for literal in {head, *body}:
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


def information_gain(tp: int, fp: int) -> float:
    if tp == 0:
        return -inf if fp == 0 else inf

    return -log(tp / (tp + fp))


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

    positives = []
    negatives = []
    constants = program.get_constants()
    for c1 in constants:
        for c2 in constants:
            clause = Clause(Literal(Atom('edge', (c1, c2))))
            if clause not in program.clauses:
                negatives.append(Literal(Atom('path', (c1, c2)), True))
            else:
                positives.append(Literal(Atom('path', (c1, c2)), False))

    pprint(positives)
    pprint(negatives)

    # learn(False, 'path', 2, program)


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
    abstract()
