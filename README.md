*This project has been created as part of the 42 curriculum by fmartins, maridos.*

# A-Maze-ing

## Description

A maze generator written in Python 3.10+: it reads a plain-text
configuration, carves either a **perfect maze** (`PERFECT=True`, one
unique path between entrance and exit) or a **Pac-Man-usable board**
(default: loop-rich, corners and centre open, dead-ends rare), draws
the mandatory **"42" pattern** with fully closed cells, and exports the
maze as one hexadecimal digit per cell.

The engine lives in the standalone, pip-installable package
[`mazegen`](docs/contract.md); the terminal application (`app/`,
parser, exporter, ASCII renderer, menu, animation) is the second half
of the team, pagente B.

**Status (05/11/2026):** Fase 1 done (backtracker, seed, "42"
pattern, animation hook) plus the Fase 2 BFS shortest-path solver.
Braiding and packaging pending (pagente A); application layer
pending (B).

## Instructions

The reusable engine works standalone today:

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate
pip install mazegen-1.0.0-py3-none-any.whl         # pending Fase 3
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()
walls = gen.grid          # dict ((row, col) -> bitmask N=1,E=2,S=4,W=8)
print(gen.pattern)        # closed cells of the "42"
print(gen.solution)       # (entry, exit, "ESEN...", BFS shortest path)
```

Full application usage (`python3 a_maze_ing.py config.txt`, Makefile
targets `install/run/debug/clean/lint/lint-strict`) lands with the
application layer of pagente B (Fases 2-3 of the team plan).

## The maze generation algorithm

**Iterative recursive backtracker** (explicit explicit-stack DFS).

Why this one:

* guarantees a *perfect* maze — a spanning tree: exactly one path
  between any two cells, no loops, no unreachable cell (except the
  "42", protected by construction);
* linear time, and carves **one cell per step**, which makes the
  animation hook (module-level `yield` per step) trivial for `app/` to
  render;
* fully deterministic under a `random.Random(seed)` — same seed,
  byte-for-byte same maze (the grading scale asks for this);
* braiding for `PERFECT=False` (removing walls at dead-ends) starts
  from this perfect base, so both modes reuse the same carver.

## The reusable part

Everything under `mazegen/` is reusable and terminal-free by design:

* `MazeGenerator(width, height, seed, perfect, entry, exit)` — raises
  typed errors (`InvalidDimensionsError`, `OutOfBoundsError`,
  `OverlappingEndpointsError`, `PatternCollisionError`) instead of
  generic failures;
* `generate()` / `steps()` (animation hook) / `grid` / `pattern`;
* `solution` — `(entry, exit, path)`; the BFS shortest route as the
  subject's section IV.5 string of concatenated `N`/`E`/`S`/`W`
  letters (e.g. `"ESENEEE"`).

See `docs/contract.md` for the full A+B contract (wall bits, owners,
phases). The package ships as `mazegen-1.0.0-py3-none-any.whl`
(plus its sdist) at the repository root, rebuildable from
`pyproject.toml` in a clean virtualenv (Fase 3).

## Team and project management

**Roles.** pagente A** (fmartins): engine (`mazegen/`) — structures,
carver, "42" pattern, solver, braiding, packaging, `pyproject.toml`,
`LICENSE.md`; pagente B (nariamaz): application (`app/` + entry
point) — config parser, hex exporter, ASCII renderer, interactive
menu, animation bonus, `Makefile`, lint/typing config. Each person
cross-tests the other's code (`tests/`): the peer evaluation checks
both halves.

**Planning and how it evolved.** Phase plan and evolving daily commit
scheme: original 8-slice split (branches `part1..part8`) was replaced
after re-reading the subject by a two-layer ownership split
(`feat/engine-*` vs `feat/app-*`, daily commits, merge into `main`
after peer review). Timeline: Fase 1 engine 03-05/11, Fase 2
solver/braids + app IO 06-10/11, Fase 3 packaging/animation 11-14/11,
Fase 4 integration + cross-tests + walkthroughs 15-18/11, buffer and
défense 19-20/11 — with regrouped priorities: the contract (bits, API,
hook) was written before any code.

**What worked well / to improve.** Contract-first avoided two
boundary bugs later (wall-bit consistency between the two sides).
Daily commit cadence kept review cheap. Improvement: bigger maze
sanity checks (3x3 rule + dead-end counts) automated as pytest in
`tests/` instead of ad-hoc scripts.

**Tools used.** git + GitHub, Makefile targets (subject), flake8 +
mypy (subject flags) + pytest + `python -m build` (pip packaging) +
venv. AI-assisted on structuring the engine code and its contract
documentation and on the commit discipline; the algorithms, contract
choices and design decisions belong to the team and both members can
explain every line during the review.

## Resources

* Subject: en.subject.pdf (attached on Intra) + `maze_analyzer.py`
* (piscina) Python modules PM01–PM10 applied module-by-module, noted in
  each commit message (`[piscina: PMxx]`)
* README pending sections (B): config-file format table, application
  instructions — marked above