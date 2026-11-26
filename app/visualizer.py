from collections.abc import Sequence
from time import sleep
from typing import Any, TextIO
import shutil
import sys

from app.colours import THEMES, DEFAULT_THEME

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
RESET = "\x1b[0m"
MENU_LINES = 7
SPEEDS = {"slow": 10, "medium": 60, "quick": 250}
SPEED_NAMES = list(SPEEDS)
DEFAULT_SPEED = "medium"

Pixel = tuple[int, int, int]
MOVES = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}


def _fg(rgb: Pixel) -> str:
    return f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def _bg(rgb: Pixel) -> str:
    return f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def style(text: str, *codes: int) -> str:
    """Applies SGR codes to the text and resets at the end."""
    start = "\x1b[" + ";".join(str(c) for c in codes) + "m"
    return f"{start}{text}{RESET}"


def clear_screen() -> None:
    """Clears the screen and the scrollback."""
    sys.stdout.write("\x1b[H\x1b[2J\x1b[3J")
    sys.stdout.flush()


def print_grid(
    grid: dict[tuple[int, int], int],
    conf: dict[str, Any],
    file: TextIO | None = None,
) -> None:
    """Plain hexadecimal output (used for the OUTPUT_FILE)."""
    for row in range(conf["HEIGHT"]):
        print("".join(f"{grid[(row, col)]:x}" for col in range(conf["WIDTH"])),
              file=file)


def path_to_cells(
    entry: Sequence[int], directions: str
) -> list[tuple[int, int]]:
    """Turns 'NNEESW' into a list of (row, col). entry is (x, y)."""
    r, c = entry[1], entry[0]
    cells = [(r, c)]
    for d in directions:
        dr, dc = MOVES[d]
        r, c = r + dr, c + dc
        cells.append((r, c))
    return cells


def paint_path(
    pix: list[list[Pixel]],
    path: Sequence[tuple[int, int]],
    color: Pixel,
) -> None:
    """Paints the path (list of (row, col)) directly on the pixel matrix."""
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        pix[r1 + r2 + 1][c1 + c2 + 1] = color
    for r, c in path:
        pix[2 * r + 1][2 * c + 1] = color


def print_maze(
    grid: dict[tuple[int, int], int],
    conf: dict[str, Any],
    path: Sequence[tuple[int, int]] = (),
    theme: str = DEFAULT_THEME,
) -> None:
    colors = THEMES[theme]
    rows, cols = conf["HEIGHT"], conf["WIDTH"]
    h, w = 2 * rows + 1, 2 * cols + 1
    pix = [[colors["wall"]] * w for _ in range(h)]

    for r in range(rows):
        for c in range(cols):
            v = grid[(r, c)]
            y, x = 2 * r + 1, 2 * c + 1
            pix[y][x] = colors["pattern"] if v == 0xF else colors["floor"]
            if not v & NORTH:
                pix[y - 1][x] = colors["floor"]
            if not v & EAST:
                pix[y][x + 1] = colors["floor"]
            if not v & SOUTH:
                pix[y + 1][x] = colors["floor"]
            if not v & WEST:
                pix[y][x - 1] = colors["floor"]

    paint_path(pix, path, colors["path"])

    ex, ey = conf["ENTRY"]
    sx, sy = conf["EXIT"]
    pix[2 * ey + 1][2 * ex + 1] = colors["entry"]
    pix[2 * sy + 1][2 * sx + 1] = colors["exit"]

    term = shutil.get_terminal_size()
    max_x = min(w, term.columns)
    max_y = min(h, (term.lines - MENU_LINES) * 2)

    lines = []
    for y in range(0, max_y, 2):
        parts = []
        for x in range(max_x):
            parts.append(_fg(pix[y][x]))
            parts.append(_bg(pix[y + 1][x]) if y + 1 < h else "\x1b[49m")
            parts.append("▀")
        lines.append("".join(parts) + RESET + "\x1b[K")

    sys.stdout.write("\x1b[H" + "\n".join(lines) + "\x1b[J")
    sys.stdout.flush()


def animate_generation(
    gen, conf: dict[str, Any], theme: str = DEFAULT_THEME
) -> None:
    """Consumes gen.steps() and redraws the maze at each step."""
    clear_screen()
    sys.stdout.write("\x1b[?25l")
    try:
        for _ in gen.steps():
            print_maze(gen.grid, conf, theme=theme)
            sleep(1 / 100)
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h")
        sys.stdout.flush()


def animate_path(
    grid: dict[tuple[int, int], int],
    conf: dict[str, Any],
    cells: Sequence[tuple[int, int]],
    theme: str = DEFAULT_THEME,
    fps: int = SPEEDS[DEFAULT_SPEED]
) -> None:
    """Draws the path step by step, from entry to exit."""
    sys.stdout.write("\x1b[?25l")                 # hide cursor
    try:
        for i in range(2, len(cells) + 1):
            print_maze(grid, conf, path=cells[:i], theme=theme)
            sleep(1 / fps)
    finally:
        sys.stdout.write("\x1b[0m\x1b[?25h")      # restore cursor
        sys.stdout.flush()


def print_menu(theme: str, show_path: bool) -> None:
    colors = THEMES[theme]
    accent = _fg(colors["path"])

    options = [
        ("1", "Generate new maze"),
        ("2", f"{'Hide' if show_path else 'Show'} path"),
        ("3", f"Change theme ({theme})"),
        ("4", "Change path speed"),
        ("5", "Quit")
    ]
    title = " A-Maze-ing "
    inner = max(len(f" {k}  {label}") for k, label in options) + 2
    inner = max(inner, len(title) + 2)

    print("┌" + title.center(inner, "─") + "┐")

    for key, label in options:
        plain = f" {key}  {label}".ljust(inner)
        colored = plain.replace(
            key, f"{accent}\x1b[1m{key}{RESET}", 1
        )
        print("│" + colored + "│")

    print("└" + "─" * inner + "┘")
