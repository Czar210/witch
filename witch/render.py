"""Tradutor: código Python -> página HTML com os glifos.

A função central é `iter_glyphs`, que percorre os tokens uma vez (com estado,
para tratar f-strings corretamente) e produz um glifo por token. Ela nunca
levanta exceção: tokens inesperados saem com categoria 'UNHANDLED', o que os
testes usam para garantir cobertura total.
"""

import html
import io
import token as token_mod
import tokenize

from .glyphs import (COMMON_BUILTINS, KEYWORDS, SPECIAL_NAMES, is_dunder,
                     is_private)
from .marks import mark_svg
from .orb import orb_svg
from .runes import rune_svg
from .seals import seal_svg
from .theme import PAGE_CSS

_STRING_TOKENS = {"STRING", "FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"}
_SKIP = {
    tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT,
    tokenize.ENCODING, tokenize.ENDMARKER,
}


def _normalize(source):
    source = source.replace("\t", "    ")
    if not source.endswith("\n"):
        source += "\n"
    return source


def _collect_definitions(source):
    """Nomes definidos por `def`/`class` — viram selos próprios (conjurados).

    Definir é forjar o feitiço; chamar é colocar o mesmo selo. Por isso o nome
    recebe o selo tanto na definição quanto em cada uso.
    """
    names = set()
    expect = False
    try:
        for tok in tokenize.generate_tokens(io.StringIO(_normalize(source)).readline):
            if tok.type in _SKIP:
                continue
            if tok.type == tokenize.NAME and tok.string in ("def", "class"):
                expect = True
                continue
            if expect:
                if tok.type == tokenize.NAME:
                    names.add(tok.string)
                expect = False
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return names


def _summon(name, forged):
    return seal_svg(name, forged=forged)


def _string_body(s):
    i = 0
    while i < len(s) and s[i] in "rbfuRBFU":
        i += 1
    if s[i:i + 3] in ('"""', "'''"):
        return s[i + 3:-3]
    if s[i:i + 1] in ('"', "'"):
        return s[i + 1:-1]
    return s[i:]


def _special_mark(name):
    base = '<circle cx="60" cy="60" r="30" fill="none" stroke="currentColor" stroke-width="5" opacity="0.85"/>'
    if name == "self":  # a instância: ponto sólido dentro do círculo
        base += '<circle cx="60" cy="60" r="9" fill="currentColor"/>'
    else:  # cls / outros: o molde — círculo dentro do círculo
        base += '<circle cx="60" cy="60" r="9" fill="none" stroke="currentColor" stroke-width="5"/>'
        base += '<line x1="60" y1="18" x2="60" y2="30" stroke="currentColor" stroke-width="4"/>'
    return f'<svg class="specialmark" viewBox="0 0 120 120" aria-hidden="true">{base}</svg>'


def _dunder(name):
    return orb_svg(name.strip("_") or "·", frame="double")


def _private(name):
    return orb_svg(name.lstrip("_") or "·", frame="dot")


def _glyph_for(toktype, tokstr):
    """Glifo de um token isolado. (categoria, markup) ou None se inesperado.

    Nomes, números e textos viram ORBES (bolas de runas) — sem escrita em fileira.
    """
    name = token_mod.tok_name.get(toktype, "")
    if toktype == tokenize.NAME:
        if tokstr in KEYWORDS:
            return "keyword", seal_svg(tokstr)
        if tokstr in COMMON_BUILTINS:
            return "builtin", seal_svg(tokstr)
        if tokstr in SPECIAL_NAMES:
            return "special", _special_mark(tokstr)
        if is_dunder(tokstr):
            return "dunder", _dunder(tokstr)
        if is_private(tokstr):
            return "private", _private(tokstr)
        return "identifier", orb_svg(tokstr)
    if toktype == tokenize.OP:
        return "operator", mark_svg(tokstr)
    if toktype == tokenize.NUMBER:
        return "number", orb_svg(tokstr)
    if name in _STRING_TOKENS:
        return "string", orb_svg(_string_body(tokstr) or "·")
    if toktype == tokenize.COMMENT:
        return "comment", orb_svg(tokstr.lstrip("#").strip() or "·")
    return None


def iter_glyphs(source):
    """Produz (row, categoria, markup, original) para cada token desenhável.

    Trata f-strings (PEP 701): mostra a expressão interpolada por dentro, com o
    texto literal e as chaves `{ }` em verde. Nunca levanta exceção.
    """
    defined = _collect_definitions(source)
    reader = io.StringIO(_normalize(source)).readline
    fdepth = 0
    forge_next = False  # o próximo NAME é o ponto de definição (def/class NAME)
    for tok in tokenize.generate_tokens(reader):
        if tok.type in _SKIP:
            continue
        nm = token_mod.tok_name.get(tok.type, "")
        row = tok.start[0]
        forged_here = forge_next
        forge_next = False

        if nm == "FSTRING_START":
            fdepth += 1
            yield row, "string", '<span class="qmark">ƒ❝</span>', tok.string
            continue
        if nm == "FSTRING_END":
            fdepth = max(0, fdepth - 1)
            yield row, "string", '<span class="qmark">❞</span>', tok.string
            continue
        if nm == "FSTRING_MIDDLE":
            if tok.string == "":
                continue
            yield row, "string", orb_svg(tok.string), tok.string
            continue
        if fdepth > 0 and tok.type == tokenize.OP and tok.string in ("{", "}"):
            # chave de interpolação (verde), distinta das chaves de dict
            yield row, "string", mark_svg(tok.string), tok.string
            continue

        # nome definido pelo usuário -> selo conjurado (forjado na definição)
        if (tok.type == tokenize.NAME and tok.string in defined
                and tok.string not in KEYWORDS and tok.string not in COMMON_BUILTINS):
            yield row, "summon", _summon(tok.string, forged_here), tok.string
            if tok.string in ("def", "class"):  # nunca verdadeiro, mas defensivo
                forge_next = True
            continue

        if tok.type == tokenize.NAME and tok.string in ("def", "class"):
            forge_next = True

        g = _glyph_for(tok.type, tok.string)
        if g is None:
            yield row, "UNHANDLED", f'<span class="cartouche">?{html.escape(tok.string)}</span>', tok.string
            continue
        yield row, g[0], g[1], tok.string


# ----------------------------------------------------------------- página
def _page(title, body, nav=""):
    safe = html.escape(title)
    return f"""<!doctype html>
<html lang="pt-br"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{safe}</title>
<style>{PAGE_CSS}</style></head>
<body>
<header><h1>\U0001fa84 {safe}</h1><div class="sp"></div>{nav}<button class="btn" data-toggle>mostrar texto</button></header>
{body}
<script>document.querySelectorAll('[data-toggle]').forEach(function(b){{b.onclick=function(){{document.body.classList.toggle('show-text');}};}});</script>
</body></html>"""


def render_source(source, title="grimório"):
    source = _normalize(source)
    lines = source.split("\n")

    rows = {}
    for row, cat, markup, orig in iter_glyphs(source):
        rows.setdefault(row, []).append((cat, markup, orig))

    out = []
    for n in range(1, len(lines) + 1):
        src = lines[n - 1] if n - 1 < len(lines) else ""
        indent = len(src) - len(src.lstrip(" "))
        glyphs = rows.get(n)
        if not glyphs:
            out.append('<div class="line blank">&nbsp;</div>')
            continue
        spans = []
        for cat, markup, orig in glyphs:
            t = html.escape(orig, quote=True)
            spans.append(f'<span class="glyph {cat}" data-text="{t}" title="{t}">{markup}</span>')
        out.append(f'<div class="line" style="padding-left:{indent * 0.6:.1f}em">{"".join(spans)}</div>')

    nav = '<a class="btn" href="grimorio.html">referência</a>'
    return _page(title, f'<div class="code">{"".join(out)}</div>', nav)


# ----------------------------------------------------------------- legenda
def _section(title, cells):
    return f'<div class="section"><h2>{html.escape(title)}</h2><div class="grid">{cells}</div></div>'


def _cell(cat, glyph, label):
    return f'<div class="cell {cat}"><div class="g">{glyph}</div><div class="lbl">{html.escape(label)}</div></div>'


def render_legend():
    """Folha de referência: alfabeto + todos os selos, marcas e glifos de POO."""
    sections = []

    cells = "".join(_cell("identifier", rune_svg(c), c) for c in "abcdefghijklmnopqrstuvwxyz0123456789")
    sections.append(_section("runas — alfabeto (híbrido, estilo Tolkien)", cells))

    orbs = [("identifier", "nome"), ("identifier", "calcular_total"),
            ("string", "witch"), ("number", "42")]
    cells = "".join(_cell(cat, orb_svg(t), t) for cat, t in orbs)
    sections.append(_section("orbes — cada palavra vira uma bola de runas", cells))

    cells = "".join(_cell("keyword", seal_svg(k), k) for k in sorted(KEYWORDS))
    sections.append(_section("selos — palavras-chave", cells))

    cells = "".join(_cell("builtin", seal_svg(b), b) for b in sorted(COMMON_BUILTINS))
    sections.append(_section("selos — funções e tipos", cells))

    ops = sorted(token_mod.EXACT_TOKEN_TYPES, key=lambda s: (len(s), s))
    cells = "".join(_cell("operator", mark_svg(o), o) for o in ops)
    sections.append(_section("marcas — operadores (todos do Python)", cells))

    oop = [
        ("special", _special_mark("self"), "self"),
        ("special", _special_mark("cls"), "cls"),
        ("dunder", _dunder("__init__"), "__init__"),
        ("dunder", _dunder("__repr__"), "__repr__"),
        ("private", _private("_x"), "_x"),
        ("private", _private("__cache"), "__cache"),
        ("string", '<span class="qmark" style="font-size:28px">ƒ❝…❞</span>', 'f"…"'),
    ]
    cells = "".join(_cell(cat, g, lbl) for cat, g, lbl in oop)
    sections.append(_section("POO e encapsulamento", cells))

    conj = [
        ("summon", _summon("saudar", True), "def saudar"),
        ("summon", _summon("saudar", False), "saudar()"),
        ("summon", _summon("fib", True), "def fib"),
        ("summon", _summon("Animal", True), "class Animal"),
        ("summon", _summon("classify", False), "classify()"),
    ]
    cells = "".join(_cell(cat, g, lbl) for cat, g, lbl in conj)
    sections.append(_section("feitiços conjurados — funções/classes suas", cells))

    intro = ('<div class="intro">Sem escrita: cada palavra (nome, número, texto) vira '
             'uma BOLA densa de runas. Selos para palavras-chave/funções, marcas para '
             'operadores. Dunders ganham anel duplo, atributos privados um ponto no '
             'topo, self/cls um emblema. Funções e classes que VOCÊ define viram selos '
             'próprios (rosa): forjados com anel de vínculo na definição, e o mesmo '
             'selo é colocado em cada chamada.</div>')
    return _page("grimório — referência", intro + "".join(sections))
