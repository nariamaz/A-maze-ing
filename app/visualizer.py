from typing import Any
import shutil
import sys

NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
WALL = (235, 235, 235)
FLOOR = (20, 20, 20)
RESET = "\x1b[0m"

def _fg(rgb: tuple[int, int, int]) -> str:
    return f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def _bg(rgb: tuple[int, int, int]) -> str:
    return f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"


def print_grid(grid: dict[tuple[int, int], int], conf: dict[str, Any]) -> None:
    ROWS = conf["WIDTH"]
    COLS = conf["HEIGHT"]

    for row in range(ROWS):
        line = ""
        for col in range(COLS):
            line += f"{grid[(row, col)]:x}"
        print(line)


def print_maze(grid: dict[tuple[int, int], int], conf: dict[str, Any]) -> None:
    rows, cols = conf["HEIGHT"], conf["WIDTH"]
    h, w = 2 * rows + 1, 2 * cols + 1
    wall = [[True] * w for _ in range(h)]

    for r in range(rows):
        for c in range(cols):
            v = grid[(r, c)]
            y, x = 2 * r + 1, 2 * c + 1
            wall[y][x] = False
            if not v & NORTH:
                wall[y - 1][x] = False
            if not v & EAST:
                wall[y][x + 1] = False
            if not v & SOUTH:
                wall[y + 1][x] = False
            if not v & WEST:
                wall[y][x - 1] = False

    term = shutil.get_terminal_size()
    max_x = min(w, term.columns)
    max_y = min(h, term.lines * 2)

    lines = []
    for y in range(0, max_y, 2):
        parts = []
        for x in range(max_x):
            parts.append(_fg(WALL if wall[y][x] else FLOOR))
            if y + 1 < h:
                parts.append(_bg(WALL if wall[y + 1][x] else FLOOR))
            else:
                parts.append("\x1b[49m")
            parts.append("▀")
        lines.append("".join(parts) + RESET + "\x1b[K")

    sys.stdout.write("\x1b[H" + "\n".join(lines) + "\x1b[J")
    sys.stdout.flush()