# f-strings: a expressao interpolada aparece por dentro dos glifos
name = "Selena"
level = 7
score = 0.8521
items = ["star", "moon"]
width = 10

print(f"witch: {name!r}")
print(f"level {level:03d} | {score:.1%}")
print(f"primeiro: {items[0].upper()}")
print(f"|{name:>{width}}|")
print(f"soma = {2 + 3 * level}")
