"""Atlas do projeto: lê TODO o código de um projeto e desenha UM glifo grande.

Cada função/método vira um sub-selo (reusa os selos conjurados). Layout
hierárquico: o projeto é o círculo-mestre, cada arquivo um setor, cada classe
um sub-círculo com seus métodos dentro, e funções soltas no setor. Arcos
opcionais ligam quem chama quem (grafo de chamadas, por nome).
"""

import ast
import html
import math
import pathlib
from dataclasses import dataclass, field

from .runes import rune_marks
from .seals import seal_inner
from .theme import PAGE_CSS

IGNORE_DIRS = {"__pycache__", ".git", ".venv", "venv", "env", "node_modules",
               "build", "dist", ".mypy_cache", ".pytest_cache", ".tox"}

# raios (no espaço do viewBox 1400)
SIZE = 1400
C = 700
MR = 650
FR_FUNC = 26.0
FR_CLASS = 48.0


@dataclass
class Func:
    name: str
    qual: str
    module: str
    forged: bool = True
    x: float = 0.0
    y: float = 0.0
    r: float = FR_FUNC
    calls: set = field(default_factory=set)


@dataclass
class Cls:
    name: str
    module: str
    methods: list = field(default_factory=list)
    x: float = 0.0
    y: float = 0.0
    r: float = FR_CLASS


@dataclass
class Module:
    name: str
    funcs: list = field(default_factory=list)
    classes: list = field(default_factory=list)
    a0: float = 0.0
    a1: float = 0.0


# --------------------------------------------------------------- scanner
def _calls_in(node):
    names = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                names.add(f.id)
            elif isinstance(f, ast.Attribute):
                names.add(f.attr)
    return names


def scan_project(root):
    root = pathlib.Path(root)
    modules = []
    files = [p for p in sorted(root.rglob("*.py"))
             if not any(part in IGNORE_DIRS for part in p.parts)]
    for p in files:
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, ValueError):
            continue
        modname = str(p.relative_to(root)).replace("\\", "/")
        mod = Module(name=modname)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                mod.funcs.append(Func(node.name, f"{modname}:{node.name}",
                                      modname, calls=_calls_in(node)))
            elif isinstance(node, ast.ClassDef):
                c = Cls(node.name, modname)
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        c.methods.append(Func(
                            sub.name, f"{modname}:{node.name}.{sub.name}",
                            modname, forged=(sub.name == "__init__"),
                            r=14.0, calls=_calls_in(sub)))
                mod.classes.append(c)
        if mod.funcs or mod.classes:
            modules.append(mod)
    return modules


# --------------------------------------------------------------- layout
def _place_methods(c):
    n = len(c.methods)
    if n == 0:
        return
    rr = c.r * 0.6
    mr = max(8.0, min(15.0, math.pi * rr / n * 0.85))
    for i, meth in enumerate(c.methods):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        meth.x = c.x + rr * math.cos(ang)
        meth.y = c.y + rr * math.sin(ang)
        meth.r = mr


def _place_module(m):
    items = [(f, FR_FUNC) for f in m.funcs] + [(c, FR_CLASS) for c in m.classes]
    pad = 0.02
    r = MR - 60
    a = m.a0 + pad
    row_max = 0.0
    for obj, fr in items:
        step = (2 * fr * 1.25) / max(r, 1.0)
        if a + step > m.a1 - pad and a > m.a0 + pad + 1e-9:
            r -= 2 * row_max * 1.35
            if r < 175:
                r = 175
            a = m.a0 + pad
            row_max = 0.0
            step = (2 * fr * 1.25) / max(r, 1.0)
        ang = a + step / 2
        obj.x = C + r * math.cos(ang)
        obj.y = C + r * math.sin(ang)
        a += step
        row_max = max(row_max, fr)
    for c in m.classes:
        _place_methods(c)


def layout(modules):
    def weight(m):
        return FR_FUNC * len(m.funcs) + FR_CLASS * len(m.classes) + 40

    total = sum(weight(m) for m in modules) or 1
    gap = min(0.05, 1.2 / max(len(modules), 1))
    avail = 2 * math.pi - gap * len(modules)
    a = -math.pi / 2
    for m in modules:
        span = avail * weight(m) / total
        m.a0 = a + gap / 2
        m.a1 = m.a0 + span
        a = m.a1 + gap / 2
        _place_module(m)


def _index(modules):
    by_name = {}
    for m in modules:
        for f in m.funcs:
            by_name.setdefault(f.name, []).append(f)
        for c in m.classes:
            for meth in c.methods:
                by_name.setdefault(meth.name, []).append(meth)
    return by_name


def _edges(modules, by_name):
    out, seen = [], set()
    for m in modules:
        srcs = list(m.funcs) + [meth for c in m.classes for meth in c.methods]
        for f in srcs:
            for callee in f.calls:
                targets = by_name.get(callee)
                if not targets:
                    continue
                same = [t for t in targets if t.module == f.module]
                t = (same or targets)[0]
                key = (id(f), id(t))
                if t is f or key in seen:
                    continue
                seen.add(key)
                out.append((f, t))
    return out


# --------------------------------------------------------------- svg
def _seal_at(name, x, y, rad, forged, cls=""):
    scale = rad / 100.0
    title = f"<title>{html.escape(name)}</title>"
    g = (f'<g class="aseal summon" transform="translate({x:.1f},{y:.1f}) '
         f'scale({scale:.4f}) translate(-100,-100)">{title}{seal_inner(name, forged)}</g>')
    lbl = (f'<text class="albl" x="{x:.1f}" y="{y + rad + 12:.1f}" '
           f'text-anchor="middle">{html.escape(cls + name)}</text>')
    return g + lbl


def build_svg(modules, root):
    layout(modules)
    by_name = _index(modules)
    p = []

    # moldura mestra
    p.append(f'<circle cx="{C}" cy="{C}" r="{MR + 10}" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>')
    p.append(f'<circle cx="{C}" cy="{C}" r="{MR}" fill="none" stroke="currentColor" stroke-width="2.5" opacity="0.75"/>')
    p.append(f'<circle cx="{C}" cy="{C}" r="{MR - 14}" fill="none" stroke="currentColor" stroke-width="1" opacity="0.4"/>')

    # divisórias de setor + rótulo do arquivo
    for m in modules:
        x1, y1 = C + 165 * math.cos(m.a0), C + 165 * math.sin(m.a0)
        x2, y2 = C + MR * math.cos(m.a0), C + MR * math.sin(m.a0)
        p.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="currentColor" stroke-width="0.7" opacity="0.22"/>')
        mid = (m.a0 + m.a1) / 2
        lx, ly = C + (MR - 32) * math.cos(mid), C + (MR - 32) * math.sin(mid)
        deg = math.degrees(mid)
        if 90 < (deg % 360) < 270:
            deg += 180
        p.append(f'<text class="modlbl" x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                 f'transform="rotate({deg:.1f} {lx:.1f} {ly:.1f})">{html.escape(m.name)}</text>')

    # arcos do grafo de chamadas (grupo ligável)
    e = []
    for f, t in _edges(modules, by_name):
        mx, my = (f.x + t.x) / 2, (f.y + t.y) / 2
        cx, cy = C + (mx - C) * 0.4, C + (my - C) * 0.4
        e.append(f'<path d="M{f.x:.1f},{f.y:.1f} Q{cx:.1f},{cy:.1f} {t.x:.1f},{t.y:.1f}" '
                 f'fill="none" stroke="#e6a3c7" stroke-width="1" opacity="0.6"/>')
    p.append(f'<g class="atlas-edges">{"".join(e)}</g>')

    # clusters de classe
    for m in modules:
        for c in m.classes:
            p.append(f'<circle cx="{c.x:.1f}" cy="{c.y:.1f}" r="{c.r:.1f}" fill="currentColor" opacity="0.05"/>')
            p.append(f'<circle cx="{c.x:.1f}" cy="{c.y:.1f}" r="{c.r:.1f}" fill="none" stroke="#9bb0d8" stroke-width="1.3" opacity="0.65"/>')
            p.append(_seal_at(c.name, c.x, c.y, c.r * 0.32, True))
            for meth in c.methods:
                p.append(_seal_at(meth.name, meth.x, meth.y, meth.r, meth.forged))

    # funções soltas
    for m in modules:
        for f in m.funcs:
            p.append(_seal_at(f.name, f.x, f.y, f.r, f.forged))

    # núcleo do projeto + nome em runas ao redor do anel externo
    proj = pathlib.Path(root).resolve().name or "projeto"
    p.append(_seal_at(proj, C, C, 118, True))
    chars = proj[:20]
    n = max(len(chars), 1)
    for i, ch in enumerate(chars):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        rx, ry = C + (MR + 28) * math.cos(ang), C + (MR + 28) * math.sin(ang)
        deg = math.degrees(ang) + 90
        p.append(f'<g class="summon" transform="translate({rx:.1f},{ry:.1f}) rotate({deg:.1f}) '
                 f'scale(0.16) translate(-50,-70)" opacity="0.7">{rune_marks(ch)}</g>')

    return "".join(p)


_ATLAS_CSS = """
.atlaswrap{ max-width:1500px; margin:0 auto; padding:8px 16px; }
svg.atlas{ width:100%; height:auto; display:block; color:#cdd3e0; }
.atlas .summon{ color:#e6a3c7; }
.atlas .modlbl{ fill:#90a0c0; font-family:ui-monospace,Consolas,monospace; font-size:13px; opacity:.85; }
.atlas .albl{ fill:#aeb6c7; font-family:ui-monospace,Consolas,monospace; font-size:11px; opacity:0; transition:opacity .2s; }
body.show-text .atlas .albl{ opacity:.92; }
.atlas-edges{ opacity:0; transition:opacity .25s; }
body.show-edges .atlas-edges{ opacity:.6; }
header .sub{ color:#7c8597; font-size:12px; margin-right:8px; }
"""


def _atlas_page(title, subtitle, svg_inner):
    safe = html.escape(title)
    return f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe}</title>
<style>{PAGE_CSS}{_ATLAS_CSS}</style></head>
<body>
<header><h1>\U0001fa84 {safe}</h1><div class="sp"></div>
<span class="sub">{html.escape(subtitle)}</span>
<button class="btn" data-edges>mostrar invocações</button>
<button class="btn" data-toggle>mostrar nomes</button></header>
<div class="atlaswrap"><svg class="atlas" viewBox="0 0 {SIZE} {SIZE}" xmlns="http://www.w3.org/2000/svg">{svg_inner}</svg></div>
<script>
document.querySelectorAll('[data-toggle]').forEach(function(b){{b.onclick=function(){{document.body.classList.toggle('show-text');}};}});
document.querySelectorAll('[data-edges]').forEach(function(b){{b.onclick=function(){{document.body.classList.toggle('show-edges');}};}});
</script>
</body></html>"""


def render_atlas(root):
    modules = scan_project(root)
    nfun = sum(len(m.funcs) + sum(len(c.methods) for c in m.classes) for m in modules)
    ncls = sum(len(m.classes) for m in modules)
    name = pathlib.Path(root).resolve().name
    subtitle = f"{len(modules)} arquivos · {nfun} feitiços · {ncls} classes"
    return _atlas_page(f"atlas — {name}", subtitle, build_svg(modules, root))
