import itertools
from typing import Dict, List


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

    # return [' '.join(rule) for rule in rules]


if __name__ == '__main__':
    # print(get(1))
    # for i in range(1, 5):
    #     print(get(i))
    #     print()

    for i, rule in enumerate(play('r', 2, {'p': 2, 'q': 1}, 2)):
        print(i, '-', rule)
