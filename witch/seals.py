"""Selos: círculos mágicos para palavras-chave e funções.

Para que cada selo seja visivelmente DISTINTO dos outros, há 8 arquétipos
(famílias de silhueta) escolhidos por hash do nome. Dentro de cada arquétipo
os parâmetros também variam por hash, e uma runa central (a primeira letra)
ancora a identidade. Tudo determinístico: `def` tem sempre o mesmo selo.
"""

import math

from ._rand import Stream
from .runes import rune_marks

TAU = math.tau


# ---------------------------------------------------------------- primitivos
def _P(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _line(x1, y1, x2, y2, w=1.0, op=0.7):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="currentColor" stroke-width="{w}" opacity="{op}" stroke-linecap="round"/>')


def _circle(cx, cy, r, w=0.0, op=0.7, fill=False):
    if fill:
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="currentColor" opacity="{op}"/>'
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
            f'stroke="currentColor" stroke-width="{w}" opacity="{op}"/>')


def _ringdots(r, n, dot=2.2, op=0.7, rot=0.0):
    return "".join(_circle(*_P(100, 100, r, rot + i * TAU / n), dot, op, True) for i in range(n))


def _poly_d(cx, cy, r, sides, rot):
    pts = [_P(cx, cy, r, rot + i * TAU / sides) for i in range(sides)]
    return (f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
            + "".join(f" L{x:.1f},{y:.1f}" for x, y in pts[1:]) + " Z")


def _poly(cx, cy, r, sides, rot, w=1.1, op=0.7):
    return f'<path d="{_poly_d(cx, cy, r, sides, rot)}" fill="none" stroke="currentColor" stroke-width="{w}" opacity="{op}"/>'


def _star(cx, cy, r, p, q, rot, w=1.1, op=0.78):
    pts = [_P(cx, cy, r, rot + i * q * TAU / p) for i in range(p)]
    d = (f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
         + "".join(f" L{x:.1f},{y:.1f}" for x, y in pts[1:]) + " Z")
    return f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="{w}" opacity="{op}"/>'


def _arc(cx, cy, r, a0, a1, w=1.0, op=0.65):
    x0, y0 = _P(cx, cy, r, a0)
    x1, y1 = _P(cx, cy, r, a1)
    large = 1 if (a1 - a0) % TAU > math.pi else 0
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}" '
            f'fill="none" stroke="currentColor" stroke-width="{w}" opacity="{op}"/>')


# ---------------------------------------------------------------- arquétipos
# Cada arquétipo recebe um Stream e devolve (partes, quer_runas_da_palavra).

def _a_lattice(s):
    sides = s.randint(3, 8)
    rot = s.rand() * TAU
    p = [_poly(100, 100, 58, sides, rot, 1.2, 0.78)]
    if s.rand() > 0.4:
        p.append(_poly(100, 100, 58, sides, rot + math.pi / sides, 0.7, 0.42))
    spokes = s.choice([sides, sides * 2])
    for i in range(spokes):
        a = rot + i * TAU / spokes
        p.append(_line(*_P(100, 100, 40, a), *_P(100, 100, 78, a), 0.6, 0.4))
    return p, True


def _a_star(s):
    p, q = s.choice([(5, 2), (7, 2), (7, 3), (8, 3), (9, 2), (9, 4), (11, 3), (12, 5)])
    rot = s.rand() * TAU
    parts = [_star(100, 100, 64, p, q, rot, 1.2, 0.82),
             _circle(100, 100, 30, 0.8, 0.4),
             _ringdots(86, p, 2.0, 0.7, rot)]
    return parts, False


def _a_square(s):
    rot = s.rand() * math.pi / 2
    parts = [_poly(100, 100, 60, 4, rot, 1.2, 0.78),
             _poly(100, 100, 60, 4, rot + math.pi / 4, 1.0, 0.55),
             _poly(100, 100, 30, 4, rot + math.pi / 4, 0.9, 0.6)]
    for i in range(4):
        a = rot + i * TAU / 4
        parts.append(_line(*_P(100, 100, 60, a), *_P(100, 100, 73, a), 0.8, 0.5))
    parts.append(_ringdots(87, 8, 2.0, 0.6, rot))
    return parts, False


def _a_radiant(s):
    n = s.choice([12, 16, 18, 24])
    rot = s.rand() * TAU
    parts = [_circle(100, 100, 34, 1.0, 0.6), _circle(100, 100, 20, 0.8, 0.5)]
    for i in range(n):
        a = rot + i * TAU / n
        r2 = 88 if i % 2 == 0 else 78
        parts.append(_line(*_P(100, 100, 36, a), *_P(100, 100, r2, a), 0.7, 0.5))
    return parts, False


def _a_orbital(s):
    k = s.choice([2, 3])
    base = s.rand() * TAU
    parts = []
    for j in range(k):
        a = base + j * TAU / k
        ox, oy = _P(100, 100, 26, a)
        rr = s.randint(34, 46)
        parts.append(_circle(ox, oy, rr, 0.85, 0.5))
        parts.append(_circle(*_P(ox, oy, rr, a), 2.6, 0.85, True))
    parts.append(_circle(100, 100, 6, 0, 0.9, True))
    parts.append(_ringdots(87, s.choice([6, 8]), 2.0, 0.55, base))
    return parts, False


def _a_sigil(s):
    pos = [_P(100, 100, 58, i * TAU / 8) for i in range(8)] + [(100, 100)]
    n = s.randint(5, 7)
    used, path, cur = set(), [], s.randint(0, 8)
    for _ in range(n):
        path.append(cur)
        used.add(cur)
        nxt = s.randint(0, 8)
        tries = 0
        while nxt in used and tries < 9:
            nxt = (nxt + 1) % 9
            tries += 1
        cur = nxt
    pts = [pos[i] for i in path]
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}" + "".join(f" L{x:.1f},{y:.1f}" for x, y in pts[1:])
    parts = [f'<path d="{d}" fill="none" stroke="currentColor" stroke-width="1.3" '
             f'opacity="0.82" stroke-linejoin="round" stroke-linecap="round"/>']
    for i in set(path):
        parts.append(_circle(*pos[i], 3.0, 0.85, True))
    return parts, True


def _a_gates(s):
    parts = []
    for r in (40, 56, 72):
        gap = s.rand() * TAU
        span = TAU * (0.55 + 0.32 * s.rand())
        parts.append(_arc(100, 100, r, gap, gap + span, 1.1, 0.72))
        parts.append(_circle(*_P(100, 100, r, gap), 2.2, 0.85, True))
        parts.append(_circle(*_P(100, 100, r, gap + span), 2.2, 0.85, True))
    for _ in range(s.choice([3, 4])):
        a = s.rand() * TAU
        parts.append(_line(*_P(100, 100, 38, a), *_P(100, 100, 74, a), 0.7, 0.45))
    return parts, True


def _a_eye(s):
    rot = math.degrees(s.rand() * TAU)
    parts = [f'<g transform="rotate({rot:.1f} 100 100)">'
             '<path d="M38,100 Q100,52 162,100 Q100,148 38,100 Z" fill="none" '
             'stroke="currentColor" stroke-width="1.3" opacity="0.8"/></g>',
             _circle(100, 100, 17, 1.0, 0.7),
             _circle(100, 100, 7, 0, 0.9, True)]
    base = math.radians(rot)
    for i in range(6):
        a = base + (i - 2.5) * 0.2
        parts.append(_line(*_P(100, 100, 62, a), *_P(100, 100, 74, a), 0.7, 0.5))
    parts.append(_ringdots(88, 10, 1.6, 0.4))
    return parts, False


_ARCH = [_a_lattice, _a_star, _a_square, _a_radiant, _a_orbital, _a_sigil, _a_gates, _a_eye]


def seal_svg(name, forged=False):
    """Selo de `name`. Se forged=True, ganha um anel de vínculo externo —
    a marca de um feitiço forjado naquele ponto (definição de função/classe)."""
    s = Stream(name)
    parts = [_circle(100, 100, 95, 0, 0.05, True),
             _circle(100, 100, 93, 1.6, 0.85)]
    if forged:
        parts.append(_circle(100, 100, 98, 2.4, 0.95))
        for i in range(12):
            a = i * TAU / 12
            parts.append(_line(*_P(100, 100, 93, a), *_P(100, 100, 99, a), 1.2, 0.7))
    if s.rand() > 0.45:
        parts.append(_circle(100, 100, 84, 0.8, 0.4))

    arch = s.randint(0, len(_ARCH) - 1)
    core, wants_words = _ARCH[arch](s)
    parts += core

    if wants_words:
        chars = name[:12]
        n = max(len(chars), 1)
        for i, ch in enumerate(chars):
            a = -math.pi / 2 + i * TAU / n
            x, y = _P(100, 100, 84, a)
            deg = math.degrees(a) + 90
            parts.append(
                f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg:.1f}) '
                f'scale(0.135) translate(-50,-70)" opacity="0.85">{rune_marks(ch)}</g>'
            )

    # runa central (primeira letra) — âncora de identidade
    parts.append(f'<g transform="translate(100,100) scale(0.36) translate(-50,-70)">{rune_marks(name[0])}</g>')

    return f'<svg class="seal-svg" viewBox="0 0 200 200" aria-hidden="true">{"".join(parts)}</svg>'
