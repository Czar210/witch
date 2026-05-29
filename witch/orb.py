"""Orbe: uma palavra inteira vira UMA bola de runas — legível.

As runas-letra ficam em ORDEM DE LEITURA ao redor do círculo (do topo, sentido
horário); palavras longas continuam num anel interno. Assim dá pra ler a palavra
seguindo o círculo. As runas ficam em pé (não giram), como uma inscrição de selo.
Determinístico, sem aleatoriedade.
"""

import math

from .runes import rune_marks

TAU = math.tau
MAX_SYMBOLS = 48


def _P(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)


def orb_inner(text, frame=None):
    chars = [c for c in str(text) if not c.isspace()][:MAX_SYMBOLS]
    if not chars:
        chars = ["·"]
    n = len(chars)

    parts = ['<circle cx="100" cy="100" r="92" fill="currentColor" opacity="0.06"/>',
             '<circle cx="100" cy="100" r="92" fill="none" stroke="currentColor" stroke-width="1.6" opacity="0.8"/>']
    if frame == "double":           # dunder: anel duplo
        parts.append('<circle cx="100" cy="100" r="83" fill="none" stroke="currentColor" stroke-width="1.0" opacity="0.5"/>')
    elif frame == "dot":            # privado: marcador no topo
        parts.append('<circle cx="100" cy="13" r="5.5" fill="currentColor" opacity="0.9"/>')

    sc = max(0.12, min(0.30, 1.05 / math.sqrt(n)))

    if n == 1:
        parts.append(f'<g transform="translate(100,100) scale({min(0.5, sc * 1.6):.3f}) '
                     f'translate(-50,-70)">{rune_marks(chars[0])}</g>')
        return "".join(parts)

    # distribui em anéis concêntricos, em ordem; o de fora primeiro
    idx = 0
    for ring_r in (78.0, 50.0, 24.0):
        if idx >= n:
            break
        cap = max(1, int(TAU * ring_r / (118 * sc)))
        k = min(cap, n - idx)
        for j in range(k):
            a = -math.pi / 2 + j * TAU / k
            x, y = _P(100, 100, ring_r, a)
            parts.append(f'<g transform="translate({x:.1f},{y:.1f}) scale({sc:.3f}) '
                         f'translate(-50,-70)" opacity="0.92">{rune_marks(chars[idx])}</g>')
            idx += 1
    return "".join(parts)


def orb_svg(text, frame=None):
    return f'<svg class="orb" viewBox="0 0 200 200" aria-hidden="true">{orb_inner(text, frame)}</svg>'
