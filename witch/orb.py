"""Orbe: uma palavra inteira vira UMA bola densa de runas (sem escrita em fileira).

As runas-letra são empacotadas dentro de um círculo por um padrão de girassol
(phyllotaxis), criando um aglomerado orgânico. O tamanho dos símbolos encolhe
conforme a palavra cresce, então o diâmetro da bola permanece ~constante — o
"símbolo de bola" é sempre preservado. Determinístico: mesma palavra, mesma bola.
"""

import math

from ._rand import Stream
from .runes import rune_marks

TAU = math.tau
GOLDEN = math.pi * (3 - 5 ** 0.5)  # ângulo áureo ~2.39996 rad
MAX_SYMBOLS = 48


def orb_inner(text, frame=None):
    chars = [c for c in str(text) if not c.isspace()][:MAX_SYMBOLS]
    if not chars:
        chars = ["·"]
    n = len(chars)
    s = Stream("orb:" + str(text))
    rot0 = s.rand() * TAU

    parts = ['<circle cx="100" cy="100" r="92" fill="currentColor" opacity="0.06"/>',
             '<circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="1.6" opacity="0.8"/>']
    if frame == "double":           # dunder: anel duplo
        parts.append('<circle cx="100" cy="100" r="83" fill="none" stroke="currentColor" stroke-width="1.0" opacity="0.5"/>')
    elif frame == "dot":            # privado: marcador no topo
        parts.append('<circle cx="100" cy="13" r="5.5" fill="currentColor" opacity="0.9"/>')

    height = max(16.0, min(86.0, 168.0 / math.sqrt(n + 1) * 0.95))
    rp = 92.0 - height * 0.42
    scale = height / 140.0

    if n == 1:
        positions = [(100.0, 100.0)]
    else:
        positions = []
        for i in range(n):
            rr = rp * math.sqrt((i + 0.5) / n)
            a = i * GOLDEN + rot0
            positions.append((100 + rr * math.cos(a), 100 + rr * math.sin(a)))

    for (x, y), ch in zip(positions, chars):
        rdeg = (s.rand() - 0.5) * 40  # leve giro orgânico, determinístico
        parts.append(
            f'<g transform="translate({x:.1f},{y:.1f}) rotate({rdeg:.1f}) '
            f'scale({scale:.3f}) translate(-50,-70)" opacity="0.92">{rune_marks(ch)}</g>'
        )
    return "".join(parts)


def orb_svg(text, frame=None):
    return f'<svg class="orb" viewBox="0 0 200 200" aria-hidden="true">{orb_inner(text, frame)}</svg>'
