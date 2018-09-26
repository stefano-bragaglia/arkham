from collections import Iterable
from random import Random

from arkham.examples.aop import Spectator

rnd = Random()


class ChaosBag(metaclass=Spectator):
    def __init__(self):
        self._tokens = [1, 2, 3, 4, 5, 6]

    @property
    def tokens(self) -> Iterable:
        return self._tokens

    def draw(self):
        return rnd.choice(self._tokens)


def triple_best(*args, **kw):
    print('~', args[0])
    selected = []
    tokens = [token for token in args[1].tokens]
    for _ in range(3):
        token = rnd.choice(tokens)
        selected.append(token)
        tokens.remove(token)
        print('>', token)

    return max(selected)


if __name__ == '__main__':
    Spectator.register(name_pattern='^draw$', after=triple_best)
    bag = ChaosBag()

    print(bag.draw())
