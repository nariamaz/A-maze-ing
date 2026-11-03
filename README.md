*This project has been created as part of the 42 curriculum by fmartins, maridos-.*

# A-Maze-ing

## Description

A maze generator written in Python 3.10+. Target product: read a
plain-text configuration, carve a **perfect maze** (`PERFECT=True`,
one unique path between entrance and exit) or a **Pac-Man-usable
board** (`PERFECT=False`: loop-rich, dead-ends rare), draw the
mandatory **"42" pattern** with fully closed cells and export the maze
as one hexadecimal digit per cell.

The engine lives in the reusable `mazegen/` package (technical
agreement in `docs/contract.md`); the terminal application (`app/`:
parser, exporter, ASCII renderer, menu, animation) is Person B's half.

**Status:** the engine core is done — iterative
backtracker, seed reproducibility, "42" pattern reserved at carving,
`steps()` animation hook. Not written yet: braiding (`PERFECT=False`),
BFS solver, wheel packaging, and the whole application layer
(Person B).

## Instructions

The reusable engine works standalone today:

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate
pip install mazegen-1.0.0-py3-none-any.whl         # wheel pending (packaging step)
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()
walls = gen.grid          # dict ((row, col) -> bitmask N=1,E=2,S=4,W=8)
print(gen.pattern)        # closed cells of the "42"
```

Full application usage (`python3 a_maze_ing.py config.txt`, Makefile
targets `install/run/debug/clean/lint/lint-strict`) lands with Person
B's application layer (pending).

## The maze generation algorithm

**Iterative recursive backtracker** (explicit-stack DFS).

Why this one:

* guarantees a *perfect* maze — a spanning tree: exactly one path
  between any two cells, no loops, no unreachable cell (except the
  "42", protected by construction);
* linear time, and carves **one cell per step**, which makes the
  animation hook (module-level `yield` per step) trivial for `app/`
  to render;
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
* `solution` — property filled by the BFS solver (`"N/E/S/W"` path
  plus its cells), still to be written.

See `docs/contract.md` for the full A+B agreement (wall bits, API
shape, folder owners). The finished package ships as
`mazegen-1.0.0-py3-none-any.whl` (plus its sdist) at the repository
root, rebuildable from `pyproject.toml` in a clean virtualenv
(packaging step).

## Team and project management

**Roles.** Person A (fmartins): engine (`mazegen/`) — structures,
carver, "42" pattern, solver, braiding, packaging, `pyproject.toml`,
`LICENSE.md`; Person B (maridos-): application (`app/` + entry
point) — config parser, hex exporter, ASCII renderer, interactive
menu, animation bonus, `Makefile`, lint/typing config. Each person
cross-tests the other's code (`tests/`): the peer evaluation checks
both halves.

**Planning and how it evolved.** We first drafted a wider task split;
after re-reading the subject we simplified to the two-layer ownership
split recorded in `docs/contract.md` — engine (`mazegen/`) vs
application (`app/`). The contract (wall bits, API shape, animation
hook) was written before any code, and both halves follow short,
explanatory commit messages.

**What worked well / to improve.** Contract-first avoided wall-bit
mismatches between the two halves. Short, patterned commits keep
review cheap. To improve: turning the ad-hoc sanity battery (wall
coherence, connectivity, seed reproducibility, dead-end counts) into
pytest tests under `tests/` as the code grows.

**Tools used.** git + GitHub, Makefile targets (subject), flake8 +
mypy (subject flags) + pytest + `python -m build` (pip packaging) +
venv. AI-assisted on structuring the engine code and its contract
documentation and on the commit discipline; the algorithms, contract
choices and design decisions belong to the team and both members can
explain every line during the review.

## Resources

* Subject PDF and `maze_analyzer.py` (attached on Intra)
* Maze generation algorithms overview: Wikipedia ("Maze generation
  algorithm") and Jamis Buck's blog ("Maze Generation: Recursive
  Backtracking")
* Python official documentation; flake8 and mypy documentation
* Pending section (Person B): config-file format table, application
  instructions — marked in Instructions
