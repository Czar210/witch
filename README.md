# 🪄 witch

Traduz código **Python** para os **glifos mágicos** no estilo de *Witch Hat Atelier*.

Cada token vira um glifo SVG desenhado proceduralmente — e determinístico:
o `if` é **sempre** o mesmo selo, então dá pra aprender a ler.

| categoria | glifo | exemplos |
|---|---|---|
| palavras-chave | **selo** — a forma diz o papel | `if` `def` `for` `return` `match` `async` |
| funções / tipos embutidos | **selo** (engrenagem, dourado/teal) | `print` `len` `range` `property` |
| **funções/classes que VOCÊ define** | **selo conjurado** (rosa) — forjado na definição, reusado em cada chamada; tamanho = linhas | `def fib` / `fib(10)` |
| operadores (todos) | **marca** | `+` `=` `==` `:=` `->` `//=` `...` `<<` |
| nomes / números / textos | **orbe** — bola legível de runas (ordem de leitura); tamanho = nº de letras | `nome` `42` `"ola"` |
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

# juntar TUDO numa bola gigante (todas as bolinhas num bolão)
python -m witch bolao . --open          # projeto inteiro
python -m witch bolao examples/oop.py   # ou um arquivo só
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

## Como ler os glifos (tudo tem significado)

Nada é arbitrário — cada propriedade visual codifica algo, e o `legend` (grimório)
é o decodificador completo:

- **Cor → categoria** (palavra-chave, função embutida, sua função/classe, variável, número, texto…)
- **Forma do selo → papel**: controle de fluxo (bifurcação), definição (bloco), salto (seta),
  valor/lógica (balança), ligação/escopo (elos), contexto/erro (portões), função embutida
  (engrenagem), sua função (faísca), sua classe (vaso).
- **Runas ao redor → o nome**, em ordem de leitura (do topo, sentido horário) — dá pra ler.
- **Tamanho → quantidade de código**: selo de função/classe ~ nº de linhas; orbe ~ nº de letras.
- **Anel de vínculo → ponto de definição**; **anel duplo → dunder**; **ponto no topo → privado**;
  **emblema ⊙/⊚ → self/cls**.

## Orbes — palavras viram bolas legíveis

Cada **palavra** (nome, número, string) vira **uma bola de runas** em **ordem de leitura**
(as runas-letra ficam em pé ao redor do círculo, do topo no sentido horário; palavras longas
continuam num anel interno). As runas seguem um alfabeto híbrido inspirado em Tolkien
(esqueleto angular + remate curvo + diacrítico). O tamanho da bola cresce com o nº de letras.

## Bolão — tudo numa bola gigante

`witch bolao <arquivo-ou-pasta>` junta **todas as bolinhas num bolão enorme**:
empacotamento de círculos recursivo onde o arquivo (ou projeto) é a bola gigante,
cada classe/função uma bola média dentro dela, e cada token uma bolinha-folha
(o mesmo selo/orbe/marca). O empacotamento é *front-chain* (como o `d3.pack`),
rápido e justo. Para projetos grandes, bolinhas minúsculas viram pontos coloridos
(nível de detalhe) — o projeto inteiro vira uma galáxia pontilhista aninhada,
leve o bastante pra abrir no navegador.

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
  bolao.py     junta tudo numa bola gigante (circle-packing recursivo + LOD)
  runner.py    executa o .py
  cli.py       interface de linha de comando
examples/      hello, oop, fstrings, kitchen_sink (todos executáveis)
tests/         run_tests.py (suíte salva)
```
