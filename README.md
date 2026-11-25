*This project has been created as part of the 42 curriculum by fmartins, maridos-.*

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
parser, exporter, terminal renderer, menu, animation) is the second
half of the team, pagente B.

## Instructions

### Engine

The reusable engine works standalone:

```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\Activate
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=21, height=15, seed=42)
gen.generate()
walls = gen.grid          # dict ((row, col) -> bitmask N=1,E=2,S=4,W=8)
print(gen.pattern)        # closed cells of the "42"
print(gen.solution)       # (entry, exit, "ESEN...", BFS shortest path)
```

### Application

```bash
python3 a_maze_ing.py config.txt
```

If no argument is given, `config.txt` is used. Any configuration or
generation error is printed as `ERROR: <message>` and the program exits
with status 1, without a traceback. Makefile targets:
`install`, `run`, `debug`, `clean`, `lint`, `lint-strict`.

### Configuration file format

One `KEY=VALUE` pair per line. Empty lines and everything after a `#`
are ignored. Keys are case-insensitive (stored in upper case).

| Key           | Type                | Required | Rules                                           |
|---------------|---------------------|----------|-------------------------------------------------|
| `WIDTH`       | integer             | yes      | greater than 0 (number of columns)              |
| `HEIGHT`      | integer             | yes      | greater than 0 (number of rows)                 |
| `ENTRY`       | `x,y`               | yes      | inside the maze, different from `EXIT`          |
| `EXIT`        | `x,y`               | yes      | inside the maze, different from `ENTRY`         |
| `OUTPUT_FILE` | string              | yes      | path of the exported file                       |
| `PERFECT`     | `True` / `False`    | yes      | perfect maze or loop-rich board                 |
| `SEED`        | integer             | no       | same seed gives the same maze                   |

Example:

```
WIDTH=20
HEIGHT=25
ENTRY=14,19
EXIT=1,1
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

## The maze generation algorithm

**Iterative recursive backtracker** (explicit-stack DFS).

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
`pyproject.toml` in a clean virtualenv.

## Application layer (`app/`)

```
a_maze_ing.py        entry point: config -> generation -> export -> menu
app/
├── config.py        parsing and validation of the configuration file
├── colours.py       colour themes (data only)
└── visualizer.py    hex export, terminal rendering, animation, menu box
```

`mazegen` never imports anything from `app/`: the dependency goes only
one way (`a_maze_ing.py` -> `app/` and `mazegen`).

### Parsing and validation (`app/config.py`)

Parsing is split in two stages, so that each function has one job:

1. **Text to dictionary** (`get_config`)
   - `read_config_file` reads the lines.
   - `get_config` strips comments, splits on the first `=`, validates the
     key name (letters, `_`, `.`, `-`) and builds a `dict[str, Any]`.
   - `convert_to_value` converts each value: digits become `int`,
     `True`/`False` become `bool`, `a,b` becomes `[a, b]`, anything else
     is a string (surrounding quotes removed).
2. **Dictionary to trusted configuration** (`validate_config`)
   - checks that every mandatory key exists;
   - checks types (`WIDTH`/`HEIGHT` positive integers, `PERFECT` boolean,
     `SEED` integer when present);
   - `check_point` checks that `ENTRY` and `EXIT` are two integers inside
     `0 <= x < WIDTH` and `0 <= y < HEIGHT`;
   - checks that `ENTRY` and `EXIT` are different.

The order matters: keys exist, then types, then bounds, so each check
can rely on the previous one. Every problem raises `ValueError` with a
message that includes the line number or the key name. The entry point
catches it in a single `except Exception` and prints `ERROR: ...`.

### Output file (`print_grid`)

`print_grid` writes one hexadecimal digit per cell, one maze row per
line (`HEIGHT` lines of `WIDTH` digits). Each digit is the wall bitmask
of the cell: `N=1`, `E=2`, `S=4`, `W=8`, and a set bit means a closed
wall. It prints plain text with no colour codes, which is why it is
separate from the terminal renderer. After the grid, the file contains
the entry, the exit and the shortest path string (`N`/`E`/`S`/`W`), all
taken from `gen.solution`.

### Terminal rendering (`app/visualizer.py`)

**Half-block technique.** A terminal character is roughly twice as tall
as it is wide. To get square "pixels", each character is the glyph `▀`
(upper half block): its *foreground* colour paints the top half and its
*background* colour paints the bottom half. Two vertically stacked
pixels therefore fit in one character.

The maze is first built as a pixel matrix of `(2*HEIGHT+1) x (2*WIDTH+1)`
entries:

- every wall pixel starts with the `wall` colour;
- cell `(r, c)` is drawn at pixel `(2r+1, 2c+1)`;
- for every bit that is **not** set in the cell, the pixel between the
  cell and its neighbour (north, east, south or west) is opened with the
  `floor` colour;
- cells whose value is `0xF` (fully closed) are the "42" pattern and get
  the `pattern` colour;
- the solution path (`paint_path`) is painted on the cells and on the
  pixel between two consecutive cells;
- entry and exit are painted last, so they always stay visible.

The matrix is then converted into text, two pixel rows per terminal line.

**Escape code flow.** All terminal control is done with ANSI escape
sequences (`ESC [ ...`, written `\x1b[`). One screen refresh looks like
this:

```
clear_screen()                 \x1b[H \x1b[2J \x1b[3J    once per menu loop
animate_*()                    \x1b[?25l                 hide cursor
   for every frame:
       \x1b[H                  go to top-left corner
       line 1 ... line N       colours + "▀" + reset + \x1b[K
       \x1b[J                  erase whatever is below the maze
   finally:  \x1b[0m \x1b[?25h reset colours, show cursor again
```

| Sequence                 | Meaning                                         |
|--------------------------|-------------------------------------------------|
| `\x1b[H`                 | move cursor to line 1, column 1                 |
| `\x1b[2J`                | clear the visible screen                        |
| `\x1b[3J`                | clear the scrollback                            |
| `\x1b[J`                 | clear from the cursor to the end of the screen  |
| `\x1b[K`                 | clear from the cursor to the end of the line    |
| `\x1b[?25l` / `\x1b[?25h`| hide / show the cursor                          |
| `\x1b[38;2;R;G;Bm`       | foreground colour (truecolor)                   |
| `\x1b[48;2;R;G;Bm`       | background colour (truecolor)                   |
| `\x1b[49m`               | default background (last odd pixel row)         |
| `\x1b[0m`                | reset all styles                                |
| `\x1b[1m`, `\x1b[7m`     | bold, reversed colours (used by the menu)       |

Design decisions:

- **A frame only moves the cursor to the top** (`\x1b[H`) instead of
  clearing the screen. Redrawing over the old frame does not flicker,
  which is what makes the animation smooth.
- **`clear_screen()` writes `\x1b[2J` before `\x1b[3J`.** Many terminals
  push the cleared screen into the scrollback, so wiping the scrollback
  must come last or the previous maze stays visible above the new one.
- **The cursor is restored in a `finally` block**, so an error in the
  middle of an animation never leaves the user with a hidden cursor.
- **Size limit.** The height is cut to `(terminal lines - MENU_LINES) * 2`
  pixels and the width to the terminal columns, so the menu is never
  pushed out of the screen. For large mazes, enlarge the terminal.
- The output file never contains these codes: it is written by
  `print_grid`, not by the renderer.

### Animations

- **Generation:** `animate_generation` consumes `MazeGenerator.steps()`
  (one carved cell per step) and redraws the grid at each step. Because
  `steps()` is a generator, `mazegen` stays free of any terminal code;
  `gen.generate()` runs the same steps silently.
- **Path:** `animate_path` draws `path[:i]` for a growing `i`, so the
  line walks from the entry to the exit. The solution string from
  `mazegen` is converted into `(row, col)` cells by `path_to_cells`.

### Colours (`app/colours.py`)

Colours live in one file, as data only. Each colour is an `(R, G, B)`
tuple (0 to 255) and each theme is a dictionary with six roles:

| Role      | Used for                       |
|-----------|--------------------------------|
| `wall`    | walls                          |
| `floor`   | corridors                      |
| `entry`   | entry cell                     |
| `exit`    | exit cell                      |
| `path`    | solution path                  |
| `pattern` | the "42" cells                 |

To add a theme, copy a block in `THEMES`, change its name and values:
it appears in the menu automatically, because the menu is built from
`THEME_NAMES`. The theme is never typed by the user (only a number is
chosen), so the renderer can index `THEMES[theme]` directly. Truecolor
needs a terminal with 24-bit colour support; keep `wall` and `floor`
clearly different for readability.

### Interactive menu

After the first generation, the program redraws the maze and a boxed
menu in a loop:

| Option | Action                                                              |
|--------|---------------------------------------------------------------------|
| 1      | generate a new maze (the file seed is used only for the first one)  |
| 2      | show or hide the shortest path (the path is animated when shown)    |
| 3      | change the colour theme (choose a number from the list)             |
| 4      | quit                                                                |

Each loop iteration clears the screen, draws the maze, then the menu
(`print_menu`). The menu title and the option numbers use the current
theme colour, and the text is padded **before** the colour codes are
added, because escape codes count as characters and would misalign the
box border. Invalid input in the theme list keeps the current theme;
generating a new maze resets the path display.

## Team and project management

**Roles.** pagente A** (fmartins): engine (`mazegen/`) — structures,
carver, "42" pattern, solver, braiding, packaging, `pyproject.toml`,
`LICENSE.md`; pagente B (nariamaz): application (`app/` + entry
point) — config parser, hex exporter, terminal renderer, interactive
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
venv. Terminal output relies on ANSI escape sequences, with no
external library.

## Resources

* Subject: en.subject.pdf (attached on Intra) + `maze_analyzer.py`
* (piscina) Python modules PM01–PM10 applied module-by-module, noted in
  each commit message (`[piscina: PMxx]`)

**Terminal and escape codes**

* [ANSI escape code](https://en.wikipedia.org/wiki/ANSI_escape_code) —
  overview of cursor, erase and colour (SGR) sequences, including
  8-bit and truecolor
* [XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html) —
  reference for `\x1b[?25l/h` (cursor visibility), `\x1b[2J`/`\x1b[3J`
  (erase) and the rest of the sequences used by the renderer
* [Block Elements (Unicode)](https://en.wikipedia.org/wiki/Block_Elements) —
  the `▀` glyph (U+2580) behind the half-block technique
* [`shutil.get_terminal_size`](https://docs.python.org/3/library/shutil.html#shutil.get_terminal_size) —
  Python documentation, used to fit the maze to the terminal

**Use of AI**

* **AI-assisted on the engine side (pagente A):** structuring the
  engine code and its contract documentation, and the commit
  discipline.
* **AI-assisted on the application side (pagente B):** Claude
  (Anthropic) was used as a tutor aid for the ANSI escape code flow, 
  and the animations.
* The algorithms, contract choices and design decisions belong to the
  team. Every AI suggestion was read, tested and adapted, and both
  members can explain the code during the review.