"""Bolão: junta TUDO numa bola gigante — todas as bolinhas num bolão só.

Empacotamento de círculos recursivo: o arquivo (ou projeto) é a bola gigante;
cada classe/função é uma bola média dentro dela; cada token é uma bolinha-folha
(o mesmo selo/orbe/marca de sempre). Hierarquia via ast (escopos por linha),
glifos via render.iter_glyphs. Determinístico.
"""

import ast
import html
import math
import pathlib
from dataclasses import dataclass, field

from .render import iter_glyphs
from .theme import PAGE_CSS

GOLDEN = math.pi * (3 - 5 ** 0.5)
GAP = 2.0
PAD = 12.0
IGNORE_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", "node_modules",
               "build", "dist", ".mypy_cache", ".pytest_cache", ".tox"}

# raio da bolinha-folha por categoria
LEAF_R = {
    "keyword": 30, "builtin": 30, "summon": 32, "identifier": 27, "number": 23,
    "string": 26, "dunder": 28, "private": 26, "special": 22, "operator": 16,
    "comment": 22,
}


@dataclass
class Scope:
    name: str
    kind: str           # project | file | class | func
    lo: int = 0
    hi: int = 10 ** 9
    children: list = field(default_factory=list)
    glyphs: list = field(default_factory=list)   # (cat, markup, r)
    items: list = field(default_factory=list)     # (kind, ref, x, y, r)
    R: float = 0.0


# --------------------------------------------------------------- construção
def build_file_scope(path):
    path = pathlib.Path(path)
    src = path.read_text(encoding="utf-8")
    root = Scope(path.name, "file")
    try:
        tree = ast.parse(src)
    except (SyntaxError, ValueError):
        return root

    def rec(node, parent):
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                kind = "class" if isinstance(ch, ast.ClassDef) else "func"
                sc = Scope(ch.name, kind, ch.lineno, ch.end_lineno or ch.lineno)
                parent.children.append(sc)
                rec(ch, sc)
            else:
                rec(ch, parent)

    rec(tree, root)

    def find(scope, row):
        for c in scope.children:
            if c.lo <= row <= c.hi:
                return find(c, row)
        return scope

    for row, cat, markup, _ in iter_glyphs(src):
        if not markup.startswith("<svg"):
            continue
        find(root, row).glyphs.append((cat, markup, float(LEAF_R.get(cat, 24))))
    return root


# --------------------------------------------------------------- packing
# Empacotamento de círculos por "front-chain" (algoritmo de Wang et al., como o
# d3.packSiblings): coloca cada círculo tangente a dois da frente, mantendo a
# cadeia de borda. O(n·√n), justo e determinístico.
class _Node:
    __slots__ = ("c", "prev", "next")

    def __init__(self, c):
        self.c = c
        self.prev = self
        self.next = self


def _place(b, a, c):
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    d2 = dx * dx + dy * dy
    if d2:
        a2 = (a[2] + c[2]) ** 2
        b2 = (b[2] + c[2]) ** 2
        if a2 > b2:
            x = (d2 + b2 - a2) / (2 * d2)
            y = math.sqrt(max(0.0, b2 / d2 - x * x))
            c[0] = b[0] - x * dx - y * dy
            c[1] = b[1] - x * dy + y * dx
        else:
            x = (d2 + a2 - b2) / (2 * d2)
            y = math.sqrt(max(0.0, a2 / d2 - x * x))
            c[0] = a[0] + x * dx - y * dy
            c[1] = a[1] + x * dy + y * dx
    else:
        c[0] = a[0] + c[2]
        c[1] = a[1]


def _intersects(a, b):
    dr = a[2] + b[2] - 1e-6
    if dr <= 0:
        return False
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return dr * dr > dx * dx + dy * dy


def _score(node):
    a, b = node.c, node.next.c
    ab = a[2] + b[2]
    dx = (a[0] * b[2] + b[0] * a[2]) / ab
    dy = (a[1] * b[2] + b[1] * a[2]) / ab
    return dx * dx + dy * dy


def _pack(radii):
    """Empacota círculos de raios dados; devolve (posições relativas, raio total)."""
    n = len(radii)
    if n == 0:
        return [], 20.0
    circles = [[0.0, 0.0, float(r) + GAP / 2] for r in radii]
    a = circles[0]
    a[0] = a[1] = 0.0
    if n > 1:
        b = circles[1]
        a[0] = -b[2]
        b[0] = a[2]
        b[1] = 0.0
    if n > 2:
        c = circles[2]
        _place(b, a, c)
        A, B, C = _Node(a), _Node(b), _Node(c)
        A.next = C.prev = B
        B.next = A.prev = C
        C.next = B.prev = A
        i = 3
        while i < n:
            c = circles[i]
            _place(A.c, B.c, c)
            node_c = _Node(c)
            j, k = B.next, A.prev
            sj, sk = B.c[2], A.c[2]
            collided = False
            while True:
                if sj <= sk:
                    if _intersects(j.c, c):
                        B = j
                        A.next = B
                        B.prev = A
                        collided = True
                        break
                    sj += j.c[2]
                    j = j.next
                else:
                    if _intersects(k.c, c):
                        A = k
                        A.next = B
                        B.prev = A
                        collided = True
                        break
                    sk += k.c[2]
                    k = k.prev
                if j is k.next:
                    break
            if collided:
                continue
            node_c.prev = A
            node_c.next = B
            A.next = B.prev = node_c
            B = node_c
            aa = _score(A)
            node = node_c.next
            while node is not B:
                sc = _score(node)
                if sc < aa:
                    A, aa = node, sc
                node = node.next
            B = A.next
            i += 1

    xs = [c[0] for c in circles]
    ys = [c[1] for c in circles]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    pos = [(c[0] - cx, c[1] - cy) for c in circles]
    R = max(math.hypot(x, y) + c[2] for (x, y), c in zip(pos, circles))
    return pos, R


def layout(scope):
    items = []
    for ch in scope.children:
        layout(ch)
        items.append(("scope", ch, ch.R))
    for g in scope.glyphs:
        items.append(("leaf", g, g[2]))
    pos, R = _pack([it[2] for it in items])
    scope.items = [(k, ref, x, y, r) for (x, y), (k, ref, r) in zip(pos, items)]
    scope.R = R + PAD


# --------------------------------------------------------------- desenho
def _ring(kind, depth):
    if kind in ("project", "file"):
        return "#cdd3e0", 2.4, 0.8
    if kind == "class":
        return "#9bb0d8", 1.8, 0.7
    return "#e6a3c7", 1.6, 0.65   # func


def _draw(scope, cx, cy, depth, parts, lodmin):
    col, w, op = _ring(scope.kind, depth)
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{scope.R:.1f}" fill="{col}" opacity="0.03"/>')
    parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{scope.R:.1f}" fill="none" stroke="{col}" stroke-width="{w}" opacity="{op}"/>')
    if scope.kind not in ("file", "project"):
        parts.append(f'<text class="blbl" x="{cx:.1f}" y="{cy - scope.R - 4:.1f}" '
                     f'text-anchor="middle" fill="{col}">{html.escape(scope.name)}</text>')
    for kind, ref, x, y, r in scope.items:
        if kind == "scope":
            _draw(ref, cx + x, cy + y, depth + 1, parts, lodmin)
        elif r >= lodmin:
            # bola grande o bastante: glifo completo
            cat, markup, _ = ref
            placed = markup.replace(
                "<svg ",
                f'<svg x="{cx + x - r:.1f}" y="{cy + y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" ',
                1)
            parts.append(f'<g class="{cat}">{placed}</g>')
        else:
            # bolinha minúscula: ponto colorido (nível de detalhe)
            cat = ref[0]
            parts.append(f'<g class="{cat}"><circle cx="{cx + x:.1f}" cy="{cy + y:.1f}" r="{r:.1f}" '
                         f'fill="currentColor" opacity="0.8"/><circle cx="{cx + x:.1f}" cy="{cy + y:.1f}" '
                         f'r="{r:.1f}" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.4"/></g>')


_BOLAO_CSS = """
.bolaowrap{ max-width:1500px; margin:0 auto; padding:8px 16px; }
svg.bolao{ width:100%; height:auto; display:block; color:#cdd3e0; }
.bolao .keyword{ color:#e8c468; } .bolao .builtin{ color:#5fd0c5; }
.bolao .operator{ color:#aab3c5; } .bolao .identifier{ color:#e9d9b8; }
.bolao .number{ color:#d99873; } .bolao .string{ color:#9bd17a; }
.bolao .comment{ color:#6b7488; } .bolao .dunder{ color:#c79be8; }
.bolao .private{ color:#d8c59a; } .bolao .special{ color:#86e0d0; }
.bolao .summon{ color:#e6a3c7; }
.bolao .blbl{ font-family:ui-monospace,Consolas,monospace; font-size:12px; opacity:0; transition:opacity .2s; }
body.show-text .bolao .blbl{ opacity:.9; }
header .sub{ color:#7c8597; font-size:12px; margin-right:8px; }
"""


def _page(title, subtitle, size, svg_inner):
    safe = html.escape(title)
    return f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe}</title>
<style>{PAGE_CSS}{_BOLAO_CSS}</style></head>
<body>
<header><h1>\U0001fa84 {safe}</h1><div class="sp"></div>
<span class="sub">{html.escape(subtitle)}</span>
<button class="btn" data-toggle>mostrar nomes</button></header>
<div class="bolaowrap"><svg class="bolao" viewBox="0 0 {size:.0f} {size:.0f}" xmlns="http://www.w3.org/2000/svg">{svg_inner}</svg></div>
<script>document.querySelectorAll('[data-toggle]').forEach(function(b){{b.onclick=function(){{document.body.classList.toggle('show-text');}};}});</script>
</body></html>"""


def _count_leaves(scope):
    return len(scope.glyphs) + sum(_count_leaves(c) for c in scope.children)


def render_bolao(path):
    p = pathlib.Path(path)
    if p.is_dir():
        files = [f for f in sorted(p.rglob("*.py"))
                 if not any(part in IGNORE_DIRS for part in f.parts)]
        root = Scope(p.resolve().name or "projeto", "project")
        for f in files:
            root.children.append(build_file_scope(f))
        scope_label = f"{len(files)} arquivos"
    else:
        root = build_file_scope(p)
        scope_label = p.name

    layout(root)
    margin = 50
    size = 2 * (root.R + margin)
    lodmin = root.R * 0.012   # abaixo disso, a bolinha vira só um ponto
    parts = []
    _draw(root, root.R + margin, root.R + margin, 0, parts, lodmin)
    subtitle = f"{scope_label} · {_count_leaves(root)} bolinhas num bolão"
    return _page(f"bolão — {pathlib.Path(path).resolve().name}", subtitle, size, "".join(parts))
