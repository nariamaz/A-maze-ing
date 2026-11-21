"""The "42" pattern: closed-cell digits drawn inside the maze.

Holds together the shape data, the candidate anchors and the minimum
board size, so the backtracker and the braiding pass
both protect the pattern's fully-closed cells.

The pattern is drawn with fully enclosed cells (all four masks raised).
Nothing here prints anything: `app/` calls :func:`pattern_fits` and
decides itself which console message fits its language. Anchor
candidates come sorted without depending on the generation seed.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

Coordinates = Tuple[int, int]

PATTERN_4: Tuple[str, ...] = ("#..#", "#..#", "####", "...#", "...#")
PATTERN_2: Tuple[str, ...] = ("###.", "..##", "..#.", "#...", "####")
PATTERN_HEIGHT: int = len(PATTERN_4)
GAP: int = 1
PATTERN_WIDTH: int = len(PATTERN_4[0]) + GAP + len(PATTERN_2[0])
MIN_WIDTH: int = PATTERN_WIDTH + 2   # pattern box + at least a 1-cell margin
MIN_HEIGHT: int = PATTERN_HEIGHT + 2


def pattern_fits(width: int, height: int) -> bool:
    """Tell whether a ``(width, height)`` board can host the "42"."""
    return width >= MIN_WIDTH and height >= MIN_HEIGHT


def candidate_anchors(width: int, height: int) -> List[Coordinates]:
    """Top-left corners for the pattern, closest to the centre first.

    One anchor is valid when the whole 5x9 box fits with at least one
    untouched margin row/column against the outer walls. The sort is
    purely deterministic: same sizes always give the same order.
    """
    if not pattern_fits(width, height):
        return []
    rows = range(1, height - PATTERN_HEIGHT)  # margem superior >= 1
    cols = range(1, width - PATTERN_WIDTH)    # margem esquerda >= 1
    limits = ((height - 1) / 2.0, (width - 1) / 2.0)
    anchors: List[Coordinates] = [
        (row, col) for row in rows for col in cols
    ]
    anchors.sort(key=_anchor_distance(*limits))
    return anchors


def _anchor_distance(
    centre_row: float,
    centre_col: float,
) -> Callable[[Coordinates], float]:
    """Squared distance from an anchor's pattern centre to the
    board centre.
    """
    row_off = (PATTERN_HEIGHT - 1) / 2.0
    col_off = (PATTERN_WIDTH - 1) / 2.0

    def distance(anchor: Coordinates) -> float:
        return (
            (anchor[0] + row_off - centre_row) ** 2
            + (anchor[1] + col_off - centre_col) ** 2
        )

    return distance


def anchor_bounds(anchor: Coordinates) -> Tuple[int, int, int, int]:
    """``(row_start, row_end, col_start, col_end)`` half-open box.

    Endpoint collision checks treat the whole box, not only the closed
    cells: the 1-cell gap between the two digits must also stay free
    of entry/exit cells.
    """
    row0, col0 = anchor
    return (
        row0,
        row0 + PATTERN_HEIGHT,
        col0,
        col0 + PATTERN_WIDTH,
    )


def pattern_cells(anchor: Coordinates) -> List[Coordinates]:
    """Every closed cell of the "42" (absolute) for one anchor."""
    row0, col0 = anchor
    cells: List[Coordinates] = []
    for row, (line4, line2) in enumerate(zip(PATTERN_4, PATTERN_2)):
        merged = line4 + "." * GAP + line2
        for col, mark in enumerate(merged):
            if mark == "#":
                cells.append((row0 + row, col0 + col))
    return cells
