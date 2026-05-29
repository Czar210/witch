"""Tradutor: código Python -> página HTML com os glifos.

A função central é `iter_glyphs`, que percorre os tokens uma vez (com estado,
para tratar f-strings corretamente) e produz um glifo por token. Ela nunca
levanta exceção: tokens inesperados saem com categoria 'UNHANDLED', o que os
testes usam para garantir cobertura total.
"""

import ast
import html
import io
import token as token_mod
import tokenize

from .glyphs import (COMMON_BUILTINS, KEYWORDS, ROLE_GROUPS, ROLE_LABELS,
                     SPECIAL_NAMES, is_dunder, is_private, role_of_keyword)
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
    """Funções/classes definidas pelo usuário, via ast.

    Devolve (funcs, classes, loc): conjuntos de nomes e um mapa nome -> linhas
    de código (para dimensionar o selo: tamanho = quantidade de código).
    """
    funcs, classes, loc = set(), set(), {}
    try:
        tree = ast.parse(_normalize(source))
    except (SyntaxError, ValueError):
        return funcs, classes, loc
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.add(node.name)
            loc[node.name] = max(1, (node.end_lineno or node.lineno) - node.lineno + 1)
        elif isinstance(node, ast.ClassDef):
            classes.add(node.name)
            loc[node.name] = max(1, (node.end_lineno or node.lineno) - node.lineno + 1)
    return funcs, classes, loc


def _sized(markup, px):
    """Injeta o tamanho de exibição no glifo (tamanho = quantidade de código)."""
    if markup.startswith("<svg"):
        return markup.replace("<svg ", f'<svg style="width:{px:.0f}px;height:{px:.0f}px" ', 1)
    return markup


def _glyph_px(cat, orig, loc):
    if cat in ("keyword", "builtin"):
        return 64
    if cat == "summon":                       # selo da sua função/classe ~ linhas de código
        return max(52, min(108, 48 + 1.4 * loc.get(orig, 1)))
    if cat == "operator":
        return 36
    if cat == "special":
        return 40
    nch = len([c for c in str(orig) if not c.isspace()])   # orbes ~ nº de letras
    return max(44, min(96, 40 + 3.2 * nch))


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
            return "keyword", seal_svg(tokstr, role_of_keyword(tokstr))
        if tokstr in COMMON_BUILTINS:
            return "builtin", seal_svg(tokstr, "builtin")
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
    funcs, classes, _loc = _collect_definitions(source)
    defined = funcs | classes
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
            role = "class" if tok.string in classes else "function"
            yield row, "summon", seal_svg(tok.string, role, forged_here), tok.string
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
    _f, _c, loc = _collect_definitions(source)

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
            m = _sized(markup, _glyph_px(cat, orig, loc))
            spans.append(f'<span class="glyph {cat}" data-text="{t}" title="{t}">{m}</span>')
        out.append(f'<div class="line" style="padding-left:{indent * 0.6:.1f}em">{"".join(spans)}</div>')

    nav = '<a class="btn" href="grimorio.html">referência</a>'
    return _page(title, f'<div class="code">{"".join(out)}</div>', nav)


# ----------------------------------------------------------------- legenda
def _section(title, cells):
    return f'<div class="section"><h2>{html.escape(title)}</h2><div class="grid">{cells}</div></div>'


def _cell(cat, glyph, label):
    return f'<div class="cell {cat}"><div class="g">{glyph}</div><div class="lbl">{html.escape(label)}</div></div>'


def _swatch(cat):
    return ('<svg viewBox="0 0 40 40" style="width:38px;height:38px">'
            '<circle cx="20" cy="20" r="15" fill="currentColor"/></svg>')


def render_legend():
    """O decodificador: explica o que cada coisa significa, pra dar pra LER."""
    sec = []
    intro = ('<div class="intro"><b>Como ler.</b> A <b>cor</b> diz a categoria · a '
             '<b>forma</b> do selo diz o papel · as <b>runas</b> ao redor soletram o '
             'nome (do topo, sentido horário) · o <b>tamanho</b> indica a quantidade '
             'de código · o <b>anel de vínculo</b> marca onde algo é definido.</div>')

    # 1) COR = categoria
    cats = [("keyword", "palavra-chave"), ("builtin", "função embutida"),
            ("summon", "sua função/classe"), ("identifier", "variável / nome"),
            ("number", "número"), ("string", "texto"), ("operator", "operador"),
            ("dunder", "dunder"), ("private", "privado"), ("comment", "comentário")]
    cells = "".join(f'<div class="cell {c}"><div class="g">{_swatch(c)}</div>'
                    f'<div class="lbl">{html.escape(l)}</div></div>' for c, l in cats)
    sec.append(_section("a COR diz a categoria", cells))

    # 2) FORMA = papel
    examples = {"control": "if", "definition": "def", "jump": "return",
                "value": "True", "binding": "import", "context": "try"}
    cells = []
    for role, ex in examples.items():
        kws = " ".join(ROLE_GROUPS[role])
        cells.append(f'<div class="cell keyword"><div class="g">{seal_svg(ex, role)}</div>'
                     f'<div class="lbl">{html.escape(ROLE_LABELS[role])}</div>'
                     f'<div class="sub2">{html.escape(kws)}</div></div>')
    cells.append(f'<div class="cell builtin"><div class="g">{seal_svg("print", "builtin")}</div>'
                 f'<div class="lbl">{html.escape(ROLE_LABELS["builtin"])}</div></div>')
    cells.append(f'<div class="cell summon"><div class="g">{seal_svg("minhaFn", "function")}</div>'
                 f'<div class="lbl">{html.escape(ROLE_LABELS["function"])}</div></div>')
    cells.append(f'<div class="cell summon"><div class="g">{seal_svg("MinhaClasse", "class")}</div>'
                 f'<div class="lbl">{html.escape(ROLE_LABELS["class"])}</div></div>')
    sec.append(_section("a FORMA diz o papel", "".join(cells)))

    # 3) RUNAS = nome (alfabeto)
    cells = "".join(_cell("identifier", rune_svg(c), c) for c in "abcdefghijklmnopqrstuvwxyz0123456789")
    sec.append(_section("as RUNAS soletram o nome (alfabeto)", cells))

    # 4) ORBES + TAMANHO
    cells = (_cell("string", _sized(orb_svg("oi"), 46), '"oi" — curto')
             + _cell("string", _sized(orb_svg("calcular"), 80), '"calcular" — longo')
             + _cell("identifier", _sized(orb_svg("nome"), 56), "nome")
             + _cell("number", _sized(orb_svg("42"), 48), "42"))
    sec.append(_section("ORBE: a palavra vira bola legível · TAMANHO ~ nº de letras", cells))

    # 5) MARCADORES
    mk = [("summon", _sized(seal_svg("fib", "function", True), 72), "definição (anel de vínculo)"),
          ("summon", _sized(seal_svg("fib", "function", False), 64), "chamada (sem anel)"),
          ("summon", _sized(seal_svg("calcular", "function"), 96), "função grande (mais linhas)"),
          ("dunder", _dunder("__init__"), "dunder (anel duplo)"),
          ("private", _private("_x"), "privado (ponto no topo)"),
          ("special", _special_mark("self"), "self"),
          ("special", _special_mark("cls"), "cls")]
    cells = "".join(_cell(c, g, l) for c, g, l in mk)
    sec.append(_section("marcadores · TAMANHO do selo ~ linhas de código", cells))

    # 6) OPERADORES
    ops = sorted(token_mod.EXACT_TOKEN_TYPES, key=lambda s: (len(s), s))
    cells = "".join(_cell("operator", mark_svg(o), o) for o in ops)
    sec.append(_section("operadores (marcas)", cells))

    return _page("grimório — como ler os glifos", intro + "".join(sec))
