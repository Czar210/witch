"""Alfabeto rúnico: cada letra/dígito vira uma runa angular.

A runa é montada sobre uma "haste" central (o stave, estilo rúnico) mais um
subconjunto de traços diagonais escolhido pelos bits do índice do caractere.
Como o índice é fixo por caractere, cada letra tem sempre a MESMA runa — então
dá pra aprender a ler nomes de variáveis, strings e números.
"""

# Nós numa grade 3x3 dentro de um viewBox 100 x 140.
NODES = {
    "TL": (20, 15),  "TM": (50, 15),  "TR": (80, 15),
    "ML": (20, 70),  "MM": (50, 70),  "MR": (80, 70),
    "BL": (20, 125), "BM": (50, 125), "BR": (80, 125),
}

# A haste central está sempre presente (dá coesão de "alfabeto").
_STAVE = ("TM", "BM")

# Traços opcionais, ativados pelos bits do índice do caractere.
_OPTIONAL = [
    ("TM", "TL"), ("TM", "TR"),
    ("MM", "TL"), ("MM", "TR"),
    ("MM", "BL"), ("MM", "BR"),
    ("ML", "MM"), ("MR", "MM"),
]


def rune_index(ch):
    """Índice estável por caractere: dígitos 0-9, letras 10-35, resto via ord()."""
    ch = ch.lower()
    if "0" <= ch <= "9":
        return ord(ch) - ord("0")
    if "a" <= ch <= "z":
        return ord(ch) - ord("a") + 10
    return 1 + (ord(ch) % 200)


def _rune_strokes(ch):
    bits = rune_index(ch) + 1  # +1 evita o caso "nenhum traço"
    strokes = [_STAVE]
    for i, stroke in enumerate(_OPTIONAL):
        if bits & (1 << i):
            strokes.append(stroke)
    return strokes


def rune_marks(ch):
    """Markup interno da runa híbrida (coords 100 x 140), estilo Tolkien:
    esqueleto angular (Cirth) + remate curvo no pé da haste + diacrítico
    (tehta) acima, escolhido pelo caractere."""
    strokes = _rune_strokes(ch)
    used = set()
    out = []
    for a, b in strokes:
        used.add(a)
        used.add(b)
        x1, y1 = NODES[a]
        x2, y2 = NODES[b]
        out.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="currentColor" stroke-width="7" stroke-linecap="round"/>'
        )
    for name in used:
        x, y = NODES[name]
        out.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="currentColor"/>')

    # remate curvo no pé da haste (curva só no remate)
    out.append('<path d="M50,125 q-9,8 -2,13" fill="none" '
               'stroke="currentColor" stroke-width="6" stroke-linecap="round"/>')

    # diacrítico (tehta) acima da haste, variando pelo caractere
    m = rune_index(ch) % 4
    if m == 0:
        out.append('<circle cx="50" cy="6" r="4" fill="currentColor"/>')
    elif m == 1:
        out.append('<circle cx="42" cy="6" r="3.4" fill="currentColor"/>'
                   '<circle cx="58" cy="6" r="3.4" fill="currentColor"/>')
    elif m == 2:
        out.append('<path d="M40,9 q10,-10 20,0" fill="none" '
                   'stroke="currentColor" stroke-width="5" stroke-linecap="round"/>')
    else:
        out.append('<line x1="44" y1="11" x2="56" y2="2" '
                   'stroke="currentColor" stroke-width="5" stroke-linecap="round"/>')
    return "".join(out)


def rune_svg(ch):
    """Runa completa como elemento <svg> embutível."""
    return f'<svg class="rune" viewBox="0 0 100 140" aria-hidden="true">{rune_marks(ch)}</svg>'
