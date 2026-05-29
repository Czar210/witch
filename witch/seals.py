"""Selos: círculos mágicos legíveis e com significado.

Cada selo é decodificável:
  - o MOTIVO central indica o PAPEL do token (controle, definição, salto,
    valor, ligação, contexto, função, classe, builtin) — não é mais hash;
  - as RUNAS ao redor soletram o NOME (em ordem de leitura), então dá pra ler;
  - a COR vem da categoria (definida no CSS);
  - o anel de vínculo externo (forged) marca o ponto de definição.
"""

import math

from .runes import rune_marks

TAU = math.tau
SM = ('fill="none" stroke="currentColor" stroke-width="4.5" '
      'stroke-linecap="round" stroke-linejoin="round"')


def _P(cx, cy, r, a):
    return cx + r * math.cos(a), cy + r * math.sin(a)


def _line(x1, y1, x2, y2, w=4.5, op=1.0):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="currentColor" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>')


def _circle(cx, cy, r, w=0.0, op=1.0, fill=False):
    if fill:
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="currentColor" opacity="{op}"/>'
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" '
            f'stroke="currentColor" stroke-width="{w}" opacity="{op}"/>')


def _arc(cx, cy, r, a0, a1, w=4.5, op=1.0):
    x0, y0 = _P(cx, cy, r, a0)
    x1, y1 = _P(cx, cy, r, a1)
    large = 1 if (a1 - a0) % TAU > math.pi else 0
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r:.1f},{r:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}" '
            f'fill="none" stroke="currentColor" stroke-width="{w}" opacity="{op}"/>')


# ---------------------------------------------------------------- motivos (papel)
def _dot(x, y, r=4.5):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="currentColor"/>'


def _build_motifs():
    m = {}
    # controle: bifurcação (decisão)
    m["control"] = (f'<path d="M100,140 V108 M100,108 L76,80 M100,108 L124,80" {SM}/>'
                    + _dot(76, 80) + _dot(124, 80))
    # definição: bloco forjado (moldura + núcleo)
    m["definition"] = (f'<rect x="76" y="80" width="48" height="40" rx="5" {SM}/>'
                       + _dot(100, 100, 5))
    # salto: seta pra fora
    m["jump"] = f'<path d="M100,140 V70 M82,92 L100,68 L118,92" {SM}/>'
    # valor / lógica: balança
    m["value"] = (f'<path d="M66,96 H134 M100,96 V78" {SM}/>'
                  f'<path d="M66,96 q8,16 16,0" {SM}/><path d="M118,96 q8,16 16,0" {SM}/>'
                  + _dot(100, 74))
    # ligação / escopo: elos de corrente
    m["binding"] = f'<circle cx="86" cy="100" r="17" {SM}/><circle cx="114" cy="100" r="17" {SM}/>'
    # contexto / erro: portões concêntricos (arcos)
    m["context"] = (_arc(100, 100, 22, math.radians(140), math.radians(40))
                    + _arc(100, 100, 34, math.radians(150), math.radians(30), 3.5)
                    + _arc(100, 100, 46, math.radians(160), math.radians(20), 3.0))
    # builtin: engrenagem (ferramenta)
    teeth = "".join(_line(*_P(100, 100, 20, i * TAU / 8), *_P(100, 100, 28, i * TAU / 8), 3.5)
                    for i in range(8))
    m["builtin"] = f'<circle cx="100" cy="100" r="20" {SM}/>{teeth}' + _dot(100, 100, 4)
    # sua função: explosão / faísca (feitiço lançado)
    rays = "".join(_line(*_P(100, 100, 10, i * TAU / 6), *_P(100, 100, 36, i * TAU / 6), 4.0)
                   for i in range(6))
    m["function"] = rays + _circle(100, 100, 8, 4.0)
    # sua classe: vaso (molde / contêiner)
    m["class"] = (_circle(100, 100, 14, 4.5) + _circle(100, 100, 26, 4.0)
                  + f'<path d="M82,128 H118" {SM}/>')
    return m


MOTIFS = _build_motifs()
ROLES = list(MOTIFS.keys())


def seal_inner(name, role="function", forged=False):
    """Markup interno do selo (coords 0..200, centro 100,100), sem o <svg>."""
    parts = [_circle(100, 100, 95, 0, 0.05, True),
             _circle(100, 100, 92, 1.6, 0.85),
             _circle(100, 100, 60, 0.8, 0.35)]
    if forged:
        parts.append(_circle(100, 100, 98, 2.4, 0.95))
        for i in range(12):
            a = i * TAU / 12
            parts.append(_line(*_P(100, 100, 92, a), *_P(100, 100, 99, a), 1.2, 0.7))

    parts.append(MOTIFS.get(role, MOTIFS["function"]))

    # nome em runas ao redor de um anel, em ordem de leitura (do topo, horário)
    chars = name[:14]
    n = max(len(chars), 1)
    sc = max(0.11, min(0.20, 0.24 - 0.012 * n))
    for i, ch in enumerate(chars):
        a = -math.pi / 2 + i * TAU / n
        x, y = _P(100, 100, 75, a)
        parts.append(f'<g transform="translate({x:.1f},{y:.1f}) scale({sc:.3f}) '
                     f'translate(-50,-70)" opacity="0.9">{rune_marks(ch)}</g>')
    return "".join(parts)


def seal_svg(name, role="function", forged=False):
    """Selo como elemento <svg> embutível."""
    return (f'<svg class="seal-svg" viewBox="0 0 200 200" aria-hidden="true">'
            f'{seal_inner(name, role, forged)}</svg>')
