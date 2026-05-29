# 🪄 witch

Traduz código **Python** para os **glifos mágicos** no estilo de *Witch Hat Atelier*.

Cada token vira um glifo SVG desenhado proceduralmente — e determinístico:
o `if` é **sempre** o mesmo selo, então dá pra aprender a ler.

| categoria | glifo | exemplos |
|---|---|---|
| palavras-chave | **selo** (círculo mágico) | `if` `def` `for` `return` `match` `async` |
| funções / tipos embutidos | **selo** (dourado/teal) | `print` `len` `range` `property` `staticmethod` |
| **funções/classes que VOCÊ define** | **selo conjurado** (rosa) — forjado na definição, reusado em cada chamada | `def fib` / `fib(10)` |
| operadores (todos) | **marca** | `+` `=` `==` `:=` `->` `//=` `...` `<<` |
| nomes / números / textos | **orbe** — bola densa de runas (sem escrita) | `nome` `42` `"ola"` |
| `self` / `cls` | **emblema** | ⊙ (instância) / ⊚ (molde) |
| dunders | **orbe** com anel duplo (violeta) | `__init__` `__repr__` |
| atributos privados | **orbe** com ponto no topo | `_x` `__cache` |
| f-strings | verde, com a **expressão interpolada por dentro** | `f"v={x:>{w}}"` |

## Como usar

Rode a partir desta pasta (Python 3.12+ — usa o tokenizador de f-strings do PEP 701):

```powershell
# traduzir um arquivo para glifos (gera um .html pra abrir no navegador)
python -m witch render examples/kitchen_sink.py --open

# executar de verdade (rodar os glifos)
python -m witch run examples/kitchen_sink.py

# folha de referência com TODOS os glifos (o "grimório")
python -m witch legend --open

# ler um PROJETO INTEIRO e desenhar um glifo grande (atlas)
python -m witch atlas . --open
```

Na página, o botão **"mostrar texto"** revela o token original embaixo de cada
glifo; passar o mouse também mostra o texto.

## Cobertura

Cobre **todo o Python base**, verificado por testes automatizados:
classes, herança, dunders, name-mangling/encapsulamento, `property`,
`classmethod`/`staticmethod`, `super`, decorators, `@dataclass`, f-strings
(com conversão `!r`, format spec e campos aninhados), compreensões
(lista/dict/set/gerador), `lambda`, walrus `:=`, `*args`/`**kwargs`,
desempacotamento, slicing, ternário, `with`, `try/except/else/finally`,
`for/else`, `match/case`, `global`/`nonlocal`, `assert`, geradores
(`yield`/`yield from`), `async`/`await`, `type` alias (3.12), imports, type
hints, e **todos** os 48 operadores de `token.EXACT_TOKEN_TYPES`.

> Como `run` apenas executa o `.py` por baixo, qualquer Python válido roda.
> O trabalho de cobertura é da **tradução** (todo token recebe um glifo).

## Testes

A suíte fica versionada em `tests/`:

```powershell
python tests/run_tests.py      # standalone
pytest tests/run_tests.py      # ou via pytest
```

Garante: selos bem-formados, **distintos entre si** e determinísticos; todos os
operadores com marca; runas distintas; nenhum token sem glifo (`UNHANDLED`) em
construções difíceis; HTML bem-formado; f-string destacando a expressão;
cobertura 1:1 token→glifo no `kitchen_sink`; e **todos os exemplos executando**.

## Funções como feitiços

No espírito de *Witch Hat Atelier*, um feitiço **é** um glifo, e você compõe
feitiços colocando sigilos dentro de outros:

- **Definir** (`def fib` / `class Animal`) **forja um selo próprio** para aquele
  nome — um glifo inteiro, único, cunhado do nome, em cor "conjurada" (rosa) e
  com um **anel de vínculo** externo marcando o ponto onde o feitiço foi forjado.
- **Chamar** (`fib(10)`) **coloca o mesmo selo** no corpo de quem chama — então o
  sigilo de `fib` aparece *dentro* do feitiço `main`. Mesmo feitiço = mesmo
  sigilo em todo lugar (é o que torna a linguagem aprendível e legível em escala).

## Atlas do projeto — todo o código num glifo só

`witch atlas <pasta>` lê **todos** os `.py` do projeto (via `ast`) e desenha
**um único glifo grande**: o projeto é o círculo-mestre, cada arquivo um setor,
cada classe um sub-círculo com seus métodos dentro, e cada função um sub-selo
(o mesmo selo conjurado). Dois botões na página:

- **mostrar nomes** — rótulo de cada feitiço;
- **mostrar invocações** — arcos ligando quem chama quem (o grafo de chamadas,
  por nome — heurística boa o suficiente para o mapa visual).

É a arquitetura do programa virando um selo de invocação.

## Orbes — palavras viram bolas (sem escrita)

Nada de texto em fileira: cada **palavra** (nome, número, string) vira **uma bola
densa de runas**. As runas-letra (estilo híbrido inspirado em Tolkien: esqueleto
angular + remate curvo + diacrítico acima) são empacotadas dentro de um círculo
por um padrão de girassol. Conforme a palavra cresce, os símbolos encolhem — então
o **diâmetro da bola permanece constante**: o "símbolo de bola" é sempre preservado.
`self`/`cls` têm emblema próprio; dunders ganham anel duplo; privados, um ponto no topo.

## Por que SVG e não imagem gerada por IA?

Porque uma linguagem precisa que cada token seja **sempre o mesmo desenho**.
SVG procedural é determinístico, vetorial (não pixela), editável e versionável.
O sistema é agnóstico à origem do glifo: dá pra trocar selos específicos por
arte ilustrada depois, sem refazer nada.

## Estrutura

```
witch/
  _rand.py     fluxo pseudo-aleatório determinístico (semeado pelo token)
  runes.py     alfabeto rúnico híbrido (estilo Tolkien): letras, dígitos
  orb.py       agrupa as runas de uma palavra numa bola densa (sem escrita)
  seals.py     selos / círculos mágicos — 8 arquétipos distintos por hash
  marks.py     marcas de operador (todos), incl. compositor de augmented
  glyphs.py    classificação: keyword / builtin / self-cls / dunder / privado
  render.py    Python -> HTML de glifos (com f-strings) + folha de referência
  atlas.py     lê o projeto inteiro (ast) -> UM glifo grande + grafo de chamadas
  runner.py    executa o .py
  cli.py       interface de linha de comando
examples/      hello, oop, fstrings, kitchen_sink (todos executáveis)
tests/         run_tests.py (suíte salva)
```
