# POO: heranca, dunder, property, encapsulamento
class Shape:
    species = "shape"

    def __init__(self, name):
        self.name = name
        self._sides = 0          # protegido

    def __repr__(self):
        return f"Shape({self.name!r}, {self._sides})"

    @property
    def sides(self):
        return self._sides


class Square(Shape):
    def __init__(self):
        super().__init__("square")
        self._sides = 4


s = Square()
print(s, "->", s.sides, "lados")
