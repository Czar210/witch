"""Marcas: glifos pequenos para operadores e pontuação.

Cobre todos os operadores que o Python reconhece (token.EXACT_TOKEN_TYPES).
Os comuns têm formas curadas e intuitivas; os de atribuição combinada
(`+=`, `//=`, ...) são compostos automaticamente como "símbolo base + seta de
ligação"; o resto cai num gerador procedural determinístico.
"""

import math

from ._rand import Stream

SK = 'stroke="currentColor" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"'
SK2 = 'stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"'


def _dot(x, y, r=5):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="currentColor"/>'


# Glifos base (espaço 0..120, centro 60,60). Sem o anel — adicionado depois.
_BASE = {
    "+": f'<line x1="60" y1="40" x2="60" y2="80" {SK}/><line x1="40" y1="60" x2="80" y2="60" {SK}/>',
    "-": f'<line x1="40" y1="60" x2="80" y2="60" {SK}/>',
    "*": (f'<line x1="60" y1="42" x2="60" y2="78" {SK}/>'
          f'<line x1="45" y1="51" x2="75" y2="69" {SK}/>'
          f'<line x1="75" y1="51" x2="45" y2="69" {SK}/>'),
    "/": f'<line x1="48" y1="80" x2="72" y2="40" {SK}/>',
    "//": f'<line x1="44" y1="80" x2="64" y2="40" {SK}/><line x1="58" y1="80" x2="78" y2="40" {SK}/>',
    "%": (f'<line x1="46" y1="78" x2="74" y2="42" {SK}/>'
          '<circle cx="48" cy="46" r="7" fill="none" stroke="currentColor" stroke-width="5"/>'
          '<circle cx="72" cy="74" r="7" fill="none" stroke="currentColor" stroke-width="5"/>'),
    "**": (f'<line x1="48" y1="44" x2="48" y2="76" {SK2}/><line x1="38" y1="52" x2="58" y2="68" {SK2}/><line x1="58" y1="52" x2="38" y2="68" {SK2}/>'
           f'<line x1="78" y1="44" x2="78" y2="76" {SK2}/><line x1="68" y1="52" x2="88" y2="68" {SK2}/><line x1="88" y1="52" x2="68" y2="68" {SK2}/>'),
    "=": f'<path d="M80 60 H44 M56 48 L44 60 L56 72" {SK}/>',
    "==": f'<line x1="42" y1="52" x2="78" y2="52" {SK}/><line x1="42" y1="68" x2="78" y2="68" {SK}/>',
    "!=": (f'<line x1="42" y1="52" x2="78" y2="52" {SK}/><line x1="42" y1="68" x2="78" y2="68" {SK}/>'
           f'<line x1="74" y1="42" x2="46" y2="78" {SK}/>'),
    "<": f'<path d="M72 42 L46 60 L72 78" {SK}/>',
    ">": f'<path d="M48 42 L74 60 L48 78" {SK}/>',
    "<=": f'<path d="M72 40 L48 56 L72 72" {SK}/><line x1="48" y1="82" x2="74" y2="82" {SK}/>',
    ">=": f'<path d="M48 40 L72 56 L48 72" {SK}/><line x1="46" y1="82" x2="72" y2="82" {SK}/>',
    "->": f'<path d="M40 60 H76 M64 48 L78 60 L64 72" {SK}/>',
    ":=": (_dot(44, 52) + _dot(44, 68) + f'<path d="M82 60 H58 M68 50 L58 60 L68 70" {SK}/>'),
    ":": _dot(60, 46) + _dot(60, 74),
    ";": _dot(60, 46) + f'<path d="M60 70 q6 8 -3 18" {SK}/>',
    ",": f'<path d="M60 64 q6 8 -3 20" {SK}/>' + _dot(60, 58),
    ".": _dot(60, 70),
    "...": _dot(44, 64) + _dot(60, 64) + _dot(76, 64),
    "(": f'<path d="M72 36 Q46 60 72 84" {SK}/>',
    ")": f'<path d="M48 36 Q74 60 48 84" {SK}/>',
    "[": f'<path d="M72 40 H50 V80 H72" {SK}/>',
    "]": f'<path d="M48 40 H70 V80 H48" {SK}/>',
    "{": f'<path d="M72 38 Q56 38 56 52 Q56 60 46 60 Q56 60 56 68 Q56 82 72 82" {SK}/>',
    "}": f'<path d="M48 38 Q64 38 64 52 Q64 60 74 60 Q64 60 64 68 Q64 82 48 82" {SK}/>',
    "@": ('<circle cx="60" cy="60" r="12" fill="none" stroke="currentColor" stroke-width="5"/>'
          f'<path d="M72 60 Q72 80 56 80" {SK}/>'),
    "~": f'<path d="M42 62 Q51 50 60 62 Q69 74 78 62" {SK}/>',
    "&": f'<path d="M44 76 V58 A16 16 0 0 1 76 58 V76" {SK}/>',
    "|": f'<line x1="60" y1="40" x2="60" y2="80" {SK}/>',
    "^": f'<path d="M44 72 L60 44 L76 72" {SK}/>',
    "<<": f'<path d="M62 44 L46 60 L62 76" {SK}/><path d="M78 44 L62 60 L78 76" {SK}/>',
    ">>": f'<path d="M58 44 L74 60 L58 76" {SK}/><path d="M42 44 L58 60 L42 76" {SK}/>',
    "!": f'<line x1="60" y1="42" x2="60" y2="66" {SK}/>' + _dot(60, 77),
}

# bases que aceitam o sufixo "=" (atribuição combinada)
_AUG_SKIP = {"==", "<=", ">=", "!=", ":="}


def _augment(op):
    base = _BASE.get(op[:-1], "")
    arrow = f'<path d="M76 94 H48 M56 88 L48 94 L56 100" {SK2}/>'
    return f'<g transform="translate(60,44) scale(0.6) translate(-60,-60)">{base}</g>{arrow}'


def _procedural(op):
    s = Stream("op:" + op)
    out = []
    for _ in range(s.randint(2, 3)):
        a1 = s.rand() * math.tau
        a2 = a1 + (0.5 + s.rand()) * math.pi
        out.append(_line(*(60 + 26 * math.cos(a1), 60 + 26 * math.sin(a1)),
                         *(60 + 26 * math.cos(a2), 60 + 26 * math.sin(a2)), 6, 0.85))
    out.append('<circle cx="60" cy="60" r="4" fill="currentColor"/>')
    return "".join(out)


def _line(x1, y1, x2, y2, w, op):
    return (f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
            f'stroke="currentColor" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')


def mark_svg(op):
    inner = _BASE.get(op)
    if inner is None:
        if len(op) >= 2 and op.endswith("=") and op not in _AUG_SKIP and op[:-1] in _BASE:
            inner = _augment(op)
        else:
            inner = _procedural(op)
    ring = ('<circle cx="60" cy="60" r="50" fill="currentColor" opacity="0.04"/>'
            '<circle cx="60" cy="60" r="50" fill="none" stroke="currentColor" stroke-width="1.4" opacity="0.6"/>')
    return f'<svg class="mark" viewBox="0 0 120 120" aria-hidden="true">{ring}{inner}</svg>'
