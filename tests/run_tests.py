"""Suite de testes do witch.

Roda standalone:   python tests/run_tests.py
Ou via pytest:     pytest tests/run_tests.py

Garante que:
  - todo selo/marca/runa sai bem-formado;
  - os selos sao distintos entre si e determinísticos;
  - TODOS os operadores do Python tem marca;
  - nenhum token fica sem glifo (UNHANDLED) em construcoes difíceis;
  - as paginas HTML sao bem-formadas;
  - f-strings destacam a expressao interpolada;
  - TODOS os exemplos executam de verdade (exit 0).
"""
import io
import pathlib
import re
import subprocess
import sys
import token
import tokenize

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from witch.glyphs import COMMON_BUILTINS, KEYWORDS          # noqa: E402
from witch.marks import mark_svg                            # noqa: E402
from witch.render import (iter_glyphs, render_legend,       # noqa: E402
                          render_source)
from witch.runes import rune_svg                            # noqa: E402
from witch.seals import seal_svg                            # noqa: E402

EXAMPLES = sorted((ROOT / "examples").glob("*.py"))
_SKIP = {tokenize.NEWLINE, tokenize.NL, tokenize.INDENT, tokenize.DEDENT,
         tokenize.ENCODING, tokenize.ENDMARKER}


def _wellformed(htmlstr):
    assert htmlstr.count("<svg") == htmlstr.count("</svg>"), "svg desbalanceado"
    assert htmlstr.count("<span") == htmlstr.count("</span>"), "span desbalanceado"
    # ignora textos do usuario (data-text/title) antes de procurar coordenada invalida
    stripped = re.sub(r'(?:data-text|title)="[^"]*"', "", htmlstr).lower()
    assert not re.search(r"\b(?:nan|inf)\b", stripped), "coordenada NaN/inf no SVG"
    import html.parser

    class _P(html.parser.HTMLParser):
        pass
    _P().feed(htmlstr)


def test_seals_wellformed_and_distinct():
    names = sorted(KEYWORDS | COMMON_BUILTINS)
    seen = {}
    for n in names:
        svg = seal_svg(n)
        assert svg.startswith("<svg") and "</svg>" in svg and "viewBox" in svg, n
        assert svg not in seen, f"selo de {n!r} identico ao de {seen[svg]!r}"
        seen[svg] = n


def test_seal_determinism():
    for n in ("def", "if", "print", "class", "while"):
        assert seal_svg(n) == seal_svg(n), n


def test_all_operators_have_marks():
    for o in set(token.EXACT_TOKEN_TYPES) | {"...", "!"}:
        m = mark_svg(o)
        assert m.startswith("<svg") and "</svg>" in m and "currentColor" in m, repr(o)


def test_runes_alphabet_distinct():
    runes = {c: rune_svg(c) for c in "abcdefghijklmnopqrstuvwxyz0123456789"}
    for c, r in runes.items():
        assert r.startswith("<svg") and "</svg>" in r, c
    assert len(set(runes.values())) == len(runes), "runas nao sao todas distintas"


def test_no_unhandled_tokens():
    extra = ('x = f"{a!r:>{w}}"\n'
             'y = [i for i in range(3) if i]\n'
             'z: int = 5\n'
             'async def g():\n'
             '    await x\n'
             'type Alias = list[int] | None\n')
    for src in [p.read_text(encoding="utf-8") for p in EXAMPLES] + [extra]:
        cats = [c for _, c, _, _ in iter_glyphs(src)]
        assert "UNHANDLED" not in cats, "ha token sem glifo"
        assert cats, "nenhum glifo gerado"


def test_render_examples_wellformed():
    for p in EXAMPLES:
        _wellformed(render_source(p.read_text(encoding="utf-8"), p.name))


def test_legend_wellformed():
    _wellformed(render_legend())


def test_fstring_breakout():
    src = 'x = 5\nw = 3\nprint(f"v={x:>{w}} ok")\n'
    out = render_source(src)
    assert 'data-text="x"' in out, "expressao da f-string nao foi destacada"
    assert "string" in out, "parte literal da f-string ausente"


def test_user_functions_become_seals():
    # def define o selo; a chamada coloca o mesmo selo (cor 'summon')
    src = "def saudar(nome):\n    return nome\n\nsaudar('x')\n"
    items = list(iter_glyphs(src))
    summons = [(c, mk, orig) for _, c, mk, orig in items if orig == "saudar"]
    assert len(summons) == 2, "esperava 'saudar' na definição e na chamada"
    for cat, markup, _ in summons:
        assert cat == "summon", f"'saudar' deveria ser selo conjurado, veio {cat}"
        assert "seal-svg" in markup, "deveria ser um selo (svg), nao runas"
    # a definição é forjada (anel de vínculo); a chamada não
    forged = [mk for c, mk, o in summons]
    assert any("r=\"98" in mk or 'r="98' in mk for mk in forged), "definição sem anel de vínculo"
    assert any('r="98' not in mk for mk in forged), "chamada não deveria ter anel de vínculo"


def test_token_coverage_is_one_to_one():
    src = (ROOT / "examples" / "kitchen_sink.py").read_text(encoding="utf-8")
    toks = list(tokenize.generate_tokens(io.StringIO(src + "\n").readline))
    meaningful = 0
    for t in toks:
        if t.type in _SKIP:
            continue
        if token.tok_name.get(t.type) == "FSTRING_MIDDLE" and t.string == "":
            continue
        meaningful += 1
    produced = sum(1 for _ in iter_glyphs(src))
    assert produced == meaningful, f"glifos {produced} != tokens {meaningful}"


def test_examples_execute():
    for p in EXAMPLES:
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True)
        assert r.returncode == 0, f"{p.name} falhou (exit {r.returncode}):\n{r.stderr}"


def main():
    tests = [(k, v) for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    passed, failed = 0, []
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
            passed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL  {name}: {e}")
            failed.append(name)
    print(f"\n{passed}/{len(tests)} testes passaram.")
    if failed:
        print("Falhas:", ", ".join(failed))
        sys.exit(1)
    print("Tudo verde.")


if __name__ == "__main__":
    main()
