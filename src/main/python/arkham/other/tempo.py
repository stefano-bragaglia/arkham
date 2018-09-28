import re
from collections import namedtuple
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


def get_combinations(size: int) -> List[List[int]]:
    combinations = [[]]
    for _ in range(size):
        updates = []
        for combination in combinations:
            for current in range(size):
                update = [*combination, current]
                updates.append(update)
        combinations = updates

    return combinations


def get_invariants(combinations: List[List[int]]) -> List[List[int]]:
    invariants = []
    for combination in combinations:
        mapping = {}
        invariant = []
        for index in combination:
            value = mapping.setdefault(index, len(mapping))
            invariant.append(value)
        if invariant not in invariants:
            invariants.append(invariant)

    return invariants[::-1]


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

    def learn(self, target: Literal, positives: List[Literal], negatives: List[Literal]) -> List[Clause]:
        signatures = []
        for clause in self._clauses:
            signature = (clause.head.negated, clause.head.functor, clause.head.get_arity())
            if signature not in signatures:
                signatures.append(signature)
        if (target.negated, target.functor, target.get_arity()) not in signatures:
            signatures.append((target.negated, target.functor, target.get_arity()))

        clauses = []

        body = ()

        tp, fp = 0, len(negatives)
        while tp < len(positives):
            best, value = None, -inf
            for signature in signatures:
                for indexes in get_combinations(signature[2]):
                    literal = Literal(Atom(signature[1], tuple('V%d' % i for i in indexes)), signature[0])
                    clause = Clause(target, (*body, literal))

                    if any(t not in literal.terms for t in target.terms):
                        continue

                    if target.functor == literal.functor and set(target.terms) == set(literal.terms):
                        continue

                    prog = Program((*clauses, clause, *self._clauses))
                    current_tp = sum(1 for p in positives if bool(prog.resolve(p)))
                    current_fp = sum(1 for n in negatives if not bool(prog.resolve(n)))
                    gain = information_gain(current_tp, current_fp)
                    if not best or gain > value:
                        best = clause
                        value = gain
                        tp = current_tp
                        fp = current_fp

            if best:
                clauses.append(best)

        return clauses


def information_gain(tp: int, fp: int) -> float:
    if tp == 0:
        return -inf if fp == 0 else inf

    return -log(tp / (tp + fp))


Signature = namedtuple('Signature', ['negated', 'name', 'arity'])


def get_signatures(head: Signature, program: Program) -> Tuple[Signature, ...]:
    signatures = sorted({Signature(l._negated, l.functor, l.get_arity()) for c in program.clauses for l in c.literals})
    if head not in signatures:
        signatures.append(head)

    return tuple(signatures)


def get_stubs(head: Signature, signatures: Tuple[Signature, ...], max_size: int = 2) -> List[List[Signature]]:
    stubs = [[head]]
    for _ in range(max_size):
        for stub in stubs:
            updates = []
            for signature in signatures:
                update = [*stub, signature]
                if update not in stubs and update not in updates:
                    updates.append(update)
            stubs = [*stubs, *updates]

    return stubs[1:]


def get_clauses(stubs: List[List[Signature]]) -> List[Clause]:
    clauses = []
    for stub in stubs:
        size = sum(p.arity for p in stub)
        combinations = get_combinations(size)
        invariants = get_invariants(combinations)
        for indexes in invariants:
            if indexes[:stub[0].arity] != [0, 1]:
                continue
            if any(i not in indexes[stub[0].arity:] for i in indexes[:stub[0].arity]):
                continue

            literals = []
            for signature in stub:
                terms = tuple('V%d' % indexes.pop(0) for _ in range(signature.arity))
                literal = Literal(Atom(signature.name, terms), signature.negated)
                if literal not in literals:
                    literals.append(literal)

            clause = Clause(literals[0], tuple(literals[1:]))
            if clause not in clauses:
                clauses.append(clause)

    return clauses


def learn(negated: bool, name: str, arity: int, program: Program, max_size: int = 2):
    signature = Signature(negated, name, arity)
    signatures = get_signatures(signature, program)
    stubs = get_stubs(signature, signatures, max_size)
    clauses = get_clauses(stubs)

    pprint([c for c in clauses])


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
        # Clause(Literal(Atom('q', ('X', 'Y'))), (Literal(Atom('p', ('Y', 'X'))),)),
        Clause(Literal(Atom('p', (1, 2)))),
    ))
    print(program)
    # print()
    # derivation = program.resolve(Literal(Atom('q', (2, 1))))
    # if derivation:
    #     print('YES')
    #     for step in derivation:
    #         clause = program.get_clause(step[0])
    #         subs = '{%s}' % ', '.join('%s: %s' % (k, term_repr(v)) for k, v in step[2].items())
    #         print('    ', clause, '  /  ', subs, '  /  ', step[1])
    # else:
    #     print('NO')

    result = program.learn(Literal(Atom('q', ('V0', 'V1'))), [Literal(Atom('q', (2, 1)))], [])
    for clause in result:
        print('\t', clause)


if __name__ == '__main__':
    abstract()
