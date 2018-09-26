import itertools
import re
from typing import Dict, Iterable, List, Tuple, Union

Value = Union[bool, float, int, str]
Variable = str
Term = Union[Value, Variable]
Substitutions = Dict[Variable, Term]


class Atom:
    def __init__(self, functor: str, terms: Tuple[Term, ...]):
        self._functor = functor
        self._terms = terms

    def __hash__(self) -> int:
        return hash(self._functor) ** hash(self._terms)

    def __repr__(self) -> str:
        if self._terms:
            values = []
            for term in self._terms:
                if type(term) in [bool, float, int]:
                    values.append(str(term))

                elif type(term) is str and re.match(r'[_a-zA-Z][_a-zA-Z0-9]*', term):
                    values.append(str(term))

                else:
                    values.append(repr(term))

            return '%s(%s)' % (self._functor, ', '.join(values))

        return self._functor

    @property
    def functor(self) -> str:
        return self._functor

    @property
    def terms(self) -> Iterable[Term]:
        return self._terms

    def get_arity(self) -> int:
        return len(self._terms)

    def is_ground(self) -> bool:
        for term in self._terms:
            if type(term) is str and (term[0] == '_' or term[0].isupper()):
                return False

        return True


class Literal:
    def __init__(self, atom: Atom, negated: bool = False):
        self._negated = negated
        self._atom = atom

    def __hash__(self) -> int:
        return hash(self._negated) ** hash(self._atom)

    def __repr__(self) -> str:
        if self._negated:
            return '~%s' % self._atom

        return repr(self._atom)

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


class Clause:
    def __init__(self, head: Literal, body: Tuple[Literal, ...] = ()):
        self._head = head
        self._body = body

    def __hash__(self) -> int:
        return hash(self._head) ** hash(self._body)

    def __repr__(self) -> str:
        if self._body:
            return '%s :- %s.' % (self._head, ', '.join(repr(literal) for literal in self._body))

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
        for literal in self.literals:
            if not literal.is_ground():
                return False

        return True


class Program:
    def __init__(self, clauses: Tuple[Clause, ...]):
        self._clauses = clauses

    def __hash__(self) -> int:
        return hash(self._clauses)

    def __repr__(self) -> str:
        return '\n'.join(repr(clause) for clause in self._clauses)

    @property
    def clauses(self) -> Iterable[Clause]:
        return self._clauses

    def get_facts(self) -> Iterable[Clause]:
        return (fact for fact in self._clauses if fact.is_fact())

    def get_rules(self) -> Iterable[Clause]:
        return (fact for fact in self._clauses if not fact.is_fact())

    def is_ground(self) -> bool:
        for clause in self._clauses:
            if not clause.is_ground():
                return False

        return True


def all_combinations(any_list):
    return itertools.chain.from_iterable(
        itertools.combinations(any_list, i + 1)
        for i in range(len(any_list)))


def get(n: int):
    combos = [[]]
    for _ in range(n):
        updates = []
        for combo in combos:
            for current in range(n):
                update = list(combo)
                update.append(current)
                updates.append(update)
        combos = updates

    results = []
    for combo in combos:
        result = []
        mapping = {}
        for item in combo:
            index = mapping.setdefault(item, len(mapping))
            result.append(index)
        if result not in results:
            results.append(result)

    return results


def play(head: str, arity: int, table: Dict[str, int], max_arity: int = 2) -> List[str]:
    rules = [[head]]
    table[head] = arity
    for _ in range(max_arity):
        updates = [[*r, k] for k in table for r in rules]
        rules = [*rules, *updates]

    results = []
    for rule in rules:
        size = sum(table[k] for k in rule)
        possibilities = get(size)
        for indexes in possibilities:
            if any(i not in indexes[arity:] for i in indexes[:arity]):
                continue

            literals = []
            for key in rule:
                terms = ', '.join('V%d' % indexes.pop(0) for _ in range(table[key]))
                literal = '%s(%s)' % (key, terms)
                if literal not in literals:
                    literals.append(literal)

            clause = [literals[0], ':-', *['%s,' % l for l in literals[1:-1]]] if len(literals) > 1 else []
            clause.append('%s.' % literals[-1])
            result = ' '.join(clause)
            if result not in results:
                results.append(result)

    return results


if __name__ == '__main__':
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
    print(p)

    # print(get(1))
    # for i in range(1, 5):
    #     print(get(i))
    #     print()

    # for i, rule in enumerate(play('r', 2, {'p': 2, 'q': 1}, 2)):
    #     print(i, '-', rule)
