# A-Maze-ing — contrato entre as dupla (A = motor, B = aplicação)

Legenda: **A** = motor (módulo `mazegen`), **B** = camada da aplicação,
**A+B** = compartilhado.

## 1. Pipeline (leitura do programa do B)

```
config.txt ─► [1 Parser B] ─► [2 Gerador A] ─► Maze
                                           │
                          ┌────────────────┴───────────┐
                          ▼                            ▼
                 [3 Solver BFS A]              [4 Encoder hex B]
                 caminho "N/E/S/W"             1 dígito hex/célula
                          └────────────────┬───────────┘
                                           ▼
                          [5 Escrita do arquivo B]
                                           ▼
                          [6 Render ASCII + menu B]
                (bônus: [5b Animação B] consome o hook do A)
```

Única dependência bloqueante: as etapas 4-8 do B precisam do grid do A.
Até lá, B usa um grid fixo pequeno, seguindo a convenção de bits abaixo.

## 2. Contrato técnico (imutável sem acordo dos dois)

* Bits das paredes: `N = 1, E = 2, S = 4, W = 8`; fechada = bit a 1.
* `Cell` = `(linha, coluna)`; conversão `x,y` (config) → `(y, x)` (grid)
  é feita na fronteira pelo B antes de chamar o motor.
* API do `MazeGenerator` (família maze-generator):
  * `MazeGenerator(width, height, seed=None, perfect=True, entry=None,
    exit=None)` — valida tudo no construtor (erros específicos).
  * `generate()` — constrói o labirinto inteiro de forma síncrona.
  * `steps()` — hook de animação: um `Cell` por passo de carving;
    A não conhece terminal nem `time.sleep`.
  * `grid` — dicionário `Cell -> bitmask` para TODAS as células
    (as do "42" vêm com bitmask 15, isoladas).
  * `solution` — conexão do solver: propriedade que expõe
    `mony` de entrada e saída + path `"N/E/S/W"`.
  * `pattern` — frozenset das células fechadas do "42"
    (vazio se tabuleiro pequeno demais; B avisa no console).

## 3. Estrutura de pastas com owner

```
A-Maze-ing/
├── a_maze_ing.py                   # B  — ponto de entrada, orquestra
├── config.txt                      # B  — config padrão (obrigatória)
├── Makefile                        # B  — install/run/debug/clean/lint
├── README.md                       # A+B — seções divididas (ver § 6)
├── LICENSE.md                      # A  — MIT (permite reuso/distribuição)
├── .gitignore                      # B  (A criou o mínimo aria; B expande)
├── setup.cfg                       # B  — regras do flake8 e do mypy
├── pyproject.toml                  # A  — metadados/build do pacote
├── mazegen-1.0.0-py3-none-any.whl  # A  — artefato na raiz (subject)
│
├── mazegen/                        # A  — motor reutilizável (sem I/O terminal)
│   ├── __init__.py                 # A  — exporta a API pública
│   ├── constants.py                # A+B — bits (único ponto A+B)
│   ├── errors.py                   # A  — MazeError e subclasses
│   ├── pattern42.py                # A  — geometria do "42"
│   ├── api.py                      # A  — ABC do gerador
│   ├── generator.py                # A  — backtracker + seed + hook
│   ├── braiding.py                 # A  — modo PERFECT=False (bônus)
│   └── solver.py                   # A  — BFS caminho mais curto
│
├── app/                            # B  — config, arquivos e terminal
│   ├── __init__.py
│   ├── config.py                   # B  — dataclass Config + parser
│   ├── errors.py                   # B  — ConfigError e afins
│   ├── exporter.py                 # B  — grid → hex → arquivo
│   ├── renderer.py                 # B  — desenho ASCII, cores ANSI
│   ├── animation.py                # B  — bônus: consome o hook
│   └── menu.py                     # B  — loop interativo
│
├── tests/                          # cross-tests (não submetido)
│   ├── test_generator.py           # B escreve (código do A)
│   ├── test_solver.py              # B escreve (código do A)
│   ├── test_braiding.py            # B escreve (código do A)
│   ├── test_config.py              # A escreve (código do B)
│   └── test_exporter.py            # A escreve (código do B)
└── docs/
    └── contract.md                 # A+B — este arquivo
```

`mazegen/` não importa nada de `app/`; a dependência vai só de
`app/` para `mazegen/` (o pacote precisa instalar sozinho via pip).

## 4. Cuidados para a peer evaluation

* Cada um precisa conseguir explicar a metade do outro (walkthrough mútuo).
* O 42 pode pedir uma pequena modificação ao vivo: ambos mexem em qualquer parte.
* O hook da animação ficou combinado na fase do contrato, não no final.

## 5. README por seção (owners)

| Seção | Owner |
|---|---|
| Primeira linha em itálico com os logins | A+B |
| Description, Instructions, formato do config | B |
| Algoritmo escolhido e por quê; parte reutilizável | A |
| Equipe/planejamento/ferramenta | A+B |
| Recursos + como a IA foi usada | A+B (cada um registra o seu) |
