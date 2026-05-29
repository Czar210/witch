"""Kitchen sink: exercita praticamente todo o Python base.

Roda do inicio ao fim sem dependencias externas. Serve de demo e de fixture
para os testes (tests/run_tests.py renderiza E executa este arquivo).
"""
from __future__ import annotations

import math as _math
from contextlib import contextmanager
from dataclasses import dataclass

PI: float = 3.14159
type Number = int | float          # alias de tipo (soft keyword 'type', 3.12)

GLOBAL_COUNT = 0


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def varargs(*args: int, **kwargs: str) -> tuple:
    return args, kwargs


@dataclass
class Point:
    x: int
    y: int = 0

    def dist(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5


class Animal:
    species = "unknown"

    def __init__(self, name: str, *, legs: int = 4) -> None:
        self.name = name
        self._legs = legs          # protegido
        self.__secret = 42         # name-mangling (encapsulamento)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r}, legs={self._legs})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Animal) and other.name == self.name

    @property
    def legs(self) -> int:
        return self._legs

    @legs.setter
    def legs(self, value: int) -> None:
        self._legs = max(0, value)

    @classmethod
    def make(cls, name: str) -> "Animal":
        return cls(name)

    @staticmethod
    def kingdom() -> str:
        return "Animalia"

    def reveal(self) -> int:
        return self.__secret


class Dog(Animal):
    species = "dog"

    def __init__(self, name: str) -> None:
        super().__init__(name, legs=4)

    def speak(self) -> str:
        return f"{self.name} says woof"


@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")


def gen(n):
    for i in range(n):
        yield i * i
    yield from (100, 200)


async def fetch(x):
    return x * 2


def classify(cmd):
    match cmd:
        case 0:
            return "zero"
        case int(n) if n > 0:
            return "pos"
        case [a, b]:
            return f"pair:{a},{b}"
        case {"k": v}:
            return f"dict:{v}"
        case _:
            return "other"


def use_globals():
    global GLOBAL_COUNT
    GLOBAL_COUNT += 1

    def inner():
        counter = 0

        def deeper():
            nonlocal counter
            counter += 1
            return counter
        return deeper()
    return inner()


def main() -> None:
    import asyncio

    d = Dog("Rex")
    print(d, "|", d.speak(), "| legs:", d.legs)
    d.legs = 3
    print("legs agora:", d.legs, "| secret:", d.reveal(), "| eq:", d == Dog("Rex"))
    print("kingdom:", Dog.kingdom(), "| make:", Animal.make("Generic"))
    print("point:", Point(3, 4), "dist:", Point(3, 4).dist())

    squares = [x * x for x in range(5) if x % 2 == 0]
    mapping = {k: k ** 2 for k in range(3)}
    uniq = {c for c in "banana"}
    total = sum(g for g in gen(4))
    print("comp:", squares, mapping, sorted(uniq), "total:", total)

    twice = lambda v: v * 2
    print("lambda:", twice(21))

    if (n := fib(10)) > 10:
        print("walrus fib:", n)

    nums = [1, 2, 3, 4, 5]
    print("slice:", nums[1:4], nums[::-1], nums[:2])
    a, *rest = nums
    merged = {**mapping, "extra": -1}
    print("unpack:", a, rest, "| merged:", merged, "| varargs:", varargs(1, 2, k="v"))

    print("ternary:", "par" if n % 2 == 0 else "impar")
    print("bitwise:", 6 & 3, 6 | 1, 6 ^ 2, 1 << 4, 64 >> 2, ~5)

    acc = 0
    acc += 5
    acc -= 1
    acc *= 3
    acc //= 2
    acc **= 2
    acc %= 100
    print("augmented:", acc)

    with tag("box") as t:
        print("dentro:", t)

    try:
        raise ValueError("boom")
    except ValueError as e:
        print("caught:", e)
    else:
        print("sem erro")
    finally:
        print("cleanup")

    for i in range(3):
        if i == 1:
            continue
        print("loop", i)
    else:
        print("loop done")

    print("match:", classify(0), classify(5), classify([1, 2]), classify({"k": 9}), classify("x"))
    print("async:", asyncio.run(fetch(21)))
    print("globals/nonlocal:", use_globals(), "count:", GLOBAL_COUNT)

    obj = {"a": 1}
    del obj["a"]
    assert obj == {}, "deveria estar vazio"
    print("pi:", PI, "sqrt:", _math.sqrt(16))


if __name__ == "__main__":
    main()
