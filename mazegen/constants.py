"""Shared wall encoding contract (A+B) — the single source of truth.

* Each cell stores its walls as one 4-bit bitmask (``int``).
* A closed wall raises the bit; an open passage clears it.
* Values follow the output-file format of the subject:
  ``N = 1, E = 2, S = 4, W = 8`` (piscina PM09: ``enum.IntFlag``).

`app/` may add its own helpers, but these numeric values never change
without an agreement logged in ``docs/contract.md``.
"""

from __future__ import annotations

from enum import IntFlag
from typing import Dict, Tuple

Cell = Tuple[int, int]
"""An immutable ``(row, col)`` position inside the maze grid."""


class Direction(IntFlag):
    """A wall side; ``value`` is the bit used in the maze encoding."""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8


ALL_WALLS: int = 0b1111  # == N|E|S|W;  a cell with the four walls closed
"""Bitmask of a cell whose four walls are closed (an isolated cell)."""

STEP: Dict[Direction, Tuple[int, int]] = {
    Direction.NORTH: (-1, 0),
    Direction.EAST: (0, 1),
    Direction.SOUTH: (1, 0),
    Direction.WEST: (0, -1),
}
"""Offset applied to a ``(row, col)`` cell to reach that neighbour."""

OPPOSITE: Dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
}
"""The same shared wall as seen from the neighbour cell."""
