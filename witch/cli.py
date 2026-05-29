"""CLI: witch render | run | legend."""

import argparse
import pathlib
import sys
import webbrowser

from .render import render_legend, render_source
from .runner import run_file


def _write(html_str, out, do_open):
    out = pathlib.Path(out)
    out.write_text(html_str, encoding="utf-8")
    print(f"[ok] grimorio escrito em: {out.resolve()}")
    if do_open:
        webbrowser.open(out.resolve().as_uri())


def main(argv=None):
    # console do Windows costuma ser cp1252; garante que prints não quebrem
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
        except (AttributeError, ValueError):
            pass

    p = argparse.ArgumentParser(
        prog="witch",
        description="Traduz Python para os glifos mágicos de Witch Hat Atelier.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="traduz um .py para uma página de glifos (.html)")
    r.add_argument("file")
    r.add_argument("-o", "--out", help="arquivo .html de saída")
    r.add_argument("--open", action="store_true", help="abre no navegador ao terminar")

    rn = sub.add_parser("run", help="executa um arquivo .py (rodar os glifos)")
    rn.add_argument("file")

    lg = sub.add_parser("legend", help="gera a folha de referência com todos os glifos")
    lg.add_argument("-o", "--out", default="grimorio.html")
    lg.add_argument("--open", action="store_true")

    at = sub.add_parser("atlas", help="lê um projeto inteiro e gera UM glifo grande (N subglifos)")
    at.add_argument("path", nargs="?", default=".", help="pasta do projeto (padrão: atual)")
    at.add_argument("-o", "--out", help="arquivo .html de saída")
    at.add_argument("--open", action="store_true")

    bo = sub.add_parser("bolao", help="junta tudo numa bola gigante (todas as bolinhas num bolão)")
    bo.add_argument("path", nargs="?", default=".", help="arquivo .py ou pasta (padrão: atual)")
    bo.add_argument("-o", "--out", help="arquivo .html de saída")
    bo.add_argument("--open", action="store_true")

    args = p.parse_args(argv)

    if args.cmd == "render":
        src_path = pathlib.Path(args.file)
        source = src_path.read_text(encoding="utf-8")
        out = args.out or str(src_path.with_suffix(".html"))
        _write(render_source(source, src_path.name), out, args.open)
    elif args.cmd == "run":
        sys.exit(run_file(args.file))
    elif args.cmd == "legend":
        _write(render_legend(), args.out, args.open)
    elif args.cmd == "atlas":
        from .atlas import render_atlas
        out = args.out or (pathlib.Path(args.path).resolve().name + "_atlas.html")
        _write(render_atlas(args.path), out, args.open)
    elif args.cmd == "bolao":
        from .bolao import render_bolao
        out = args.out or (pathlib.Path(args.path).resolve().stem + "_bolao.html")
        _write(render_bolao(args.path), out, args.open)


if __name__ == "__main__":
    main()
