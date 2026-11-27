"""
Terminal-based maze visualization and animation module.

This module handles the visual representation of the maze in the terminal,
including colored rendering, path visualization, generation animation,
and interactive menu display.

It uses ANSI escape sequences to control terminal colors, cursor visibility,
screen clearing and text formatting. The maze is rendered using RGB colors
defined in the app.colours module.

Constants:
    NORTH, EAST, SOUTH, WEST:
        Bitmask values representing the four possible wall directions
        of each maze cell.

    RESET:
        ANSI escape sequence that resets terminal formatting and colors.

    MENU_LINES:
        Number of terminal lines reserved for the interactive menu.
        Used to calculate the available height for maze rendering.

    SPEEDS:
        Dictionary containing the available path animation speeds:
            - slow:   10 FPS
            - medium: 60 FPS
            - quick:  250 FPS

    SPEED_NAMES:
        List containing the available animation speed names.

    DEFAULT_SPEED:
        Default animation speed, set to “medium”.

    Pixel:
        Type alias representing an RGB color as a tuple of three integers.

    MOVES:
        Dictionary mapping cardinal directions to their corresponding
        (row, column) movement offsets.

Functions:
    _fg(rgb):
        Generates an ANSI escape sequence for setting the terminal
        foreground color using RGB values.

    _bg(rgb):
        Generates an ANSI escape sequence for setting the terminal
        background color using RGB values.

    style(text, *codes):
        Applies ANSI Select Graphic Rendition (SGR) formatting codes
        to a string and resets the formatting at the end.

    clear_screen():
        Clears the terminal screen and scrollback buffer, then positions
        the cursor at the top-left corner.

    print_grid(grid, conf, file):
        Exports the maze grid as plain hexadecimal values.
        Each cell is represented by its hexadecimal wall bitmask.
        The output can be redirected to a file through the optional
        file parameter.

    path_to_cells(entry, directions):
        Converts a sequence of movement directions into a list of
        maze coordinates (row, column).

        The entry coordinate is provided in configuration format (x, y),
        while the resulting coordinates use the engine format (row, col).

    paint_path(pix, path, color):
        Draws a solution path directly onto the pixel matrix.

        Colors both the center of each visited cell and the intermediate
        pixels connecting consecutive cells.

    print_maze(grid, conf, path, theme):
        Converts the maze grid into a colored pixel matrix and renders
        it directly in the terminal.

        The rendering process:
            1. Retrieves the selected theme color palette.
            2. Creates a pixel matrix with dimensions twice the maze
               dimensions plus one.
            3. Draws cell floors, walls and connecting passages.
            4. Highlights cells with all four walls using the pattern color.
            5. Draws the solution path when provided.
            6. Highlights the entry and exit positions.
            7. Adjusts the rendering dimensions to fit the terminal.
            8. Uses ANSI foreground and background colors with Unicode
               half-block characters to render two vertical pixels
               in a single terminal character.

    animate_generation(gen, conf, theme):
        Animates the maze generation process.

        Consumes the generator’s steps() iterator, redraws the maze
        after every generation step and introduces a short delay
        between frames.

        Hides the terminal cursor during animation and restores
        terminal formatting and cursor visibility afterward.

    animate_path(grid, conf, cells, theme, fps):
        Animates the solution path from the entry to the exit.

        Progressively reveals the path by passing an increasingly
        larger portion of the cell sequence to print_maze().

        The animation speed is controlled by the fps parameter,
        which determines the delay between frames.

    print_menu(theme, show_path):
        Displays the interactive terminal menu.

        The menu provides the following options:
            1. Generate a new maze.
            2. Show or hide the solution path.
            3. Change the visualization theme.
            4. Change the path animation speed.
            5. Quit the application.

        The selected theme’s path color is used to highlight
        menu option numbers.

Rendering conventions:
    The maze engine represents cells using (row, column) coordinates.
    The configuration file represents positions using (x, y).

    The pixel matrix uses an expanded coordinate system:
        - Odd rows and columns represent cell centers.
        - Even positions between cells represent walls or passages.
        - The matrix dimensions are calculated as:
              height = 2 * maze_height + 1
              width  = 2 * maze_width + 1

    Terminal rendering uses the Unicode upper-half block character (▀)
    to display two vertically stacked pixels per terminal character.

Dependencies:
    collections.abc.Sequence:
        Provides the Sequence type for accepting ordered collections.

    time.sleep:
        Controls the delay between animation frames.

    typing.Any, typing.TextIO:
        Provides type annotations for configuration dictionaries
        and file output.

    shutil:
        Retrieves terminal dimensions.

    sys:
        Handles terminal input/output through standard output.

    app.colours:
        Provides the available theme palettes and the default theme.
"""
from collections.abc import Sequence
from time import sleep
from typing import Any, TextIO
from mazegen.generator import MazeGenerator
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
    gen: MazeGenerator,
    conf: dict[str, Any],
    theme: str = DEFAULT_THEME
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
    BOLD = "\033[1m"
    BLINK = "\033[5m"
    RESET = "\033[0m"

    inner = max(len(f" {k}  {label}") for k, label in options) + 2
    inner = max(inner, len(title) + 2)
    print("┌" + title.center(inner, "─").replace(title,
          f"{BOLD}{BLINK}{title}{RESET}", 1) + "┐")

    for key, label in options:
        plain = f" {key}  {label}".ljust(inner)
        colored = plain.replace(
            key, f"{accent}\x1b[1m{key}{RESET}", 1
        )
        print("│" + colored + "│")

    print("└" + "─" * inner + "┘")
