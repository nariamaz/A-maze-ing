"""Braiding pass: weave loops into a perfect maze.

A *perfect* maze (the backtracker) is a spanning tree: one
single route between any two cells and, as a side effect, plenty of
dead ends — cells closed on three of their four sides. Braiding is the
classic post-pass that removes cul-de-sacs by knocking one extra wall
per dead end, adding loops: the board stops being a tree, alternative
routes multiply, and the BFS shortest path of :mod:`mazegen.solver`
stops being unique.

Guards, shared with the carver and the solver:

* an outer wall is never opened (the neighbour must lie in-board);
* a protected cell — the "42" of :mod:`mazegen.pattern42` — is never
  touched, neither as the dead end itself nor as the neighbour that
  would receive the breach;
* a dead end without a safe candidate (the far end of a 1xN corridor)
  stays as it is;
* at most one new passage per dead end, and the dead-end list is
  snapshotted before any change, so an opening never cascades into
  re-treating a cell that stopped being a cul-de-sac.

Run it through ``MazeGenerator(..., perfect=False)``: both
:meth:`~mazegen.generator.MazeGenerator.generate` and
:meth:`~mazegen.generator.MazeGenerator.steps` call :func:`braid`
right after carving, reusing the carver's own random stream, so the
same seed always produces the same braided board.
"""

from __future__ import annotations

import random
from collections.abc import Iterable
from typing import Optional

from mazegen.constants import OPPOSITE, STEP, Cell, Direction


def braid(
    grid: dict[Cell, int],
    width: int,
    height: int,
    protected: Iterable[Cell] = (),
    rng: Optional[random.Random] = None,
) -> int:
    """Open one wall per dead end, weaving loops into the maze.

    A dead end is a cell with exactly three closed walls (popcount 3
    on the ``N = 1, E = 2, S = 4, W = 8`` bitmask). Each dead end is
    collected before any change, then receives at most one extra
    opening: one of its closed walls whose neighbour is in-board and
    not protected. The choice comes from *rng* over the fixed
    ``N, E, S, W`` candidate order, so an equal seed braids identically.

    Args:
        grid: Wall bitmask ``Cell -> int``, mutated in place — the
            same mapping the carver owns.
        width: Number of columns of the board.
        height: Number of rows of the board.
        protected: Cells that must never gain or lose a wall (the
            "42"); a dead end facing only protected cells stays put.
        rng: Random stream for the choice; ``None`` creates one —
            callers pass their own seeded stream for reproducibility.

    Returns:
        How many passages were opened; ``0`` means nothing was braided.

    Examples:
        A 2x2 snake whose two ends are cul-de-sacs: one loop joins
        them (the second end loses its dead-end status in the act,
        so the snapshot rule makes the pass stop there).

        >>> snake = {(0, 0): 0b1101, (0, 1): 0b0011,
        ...          (1, 0): 0b1101, (1, 1): 0b1010}
        >>> braid(snake, 2, 2)
        1
        >>> snake[(0, 0)] & int(Direction.SOUTH.value)
        0
        >>> snake[(1, 0)] & int(Direction.NORTH.value)
        0

        A 1x3 corridor: both ends have no in-board candidate wall,
        so the pass leaves every wall untouched.

        >>> corridor = {(0, 0): 0b1101, (0, 1): 0b0101, (0, 2): 0b0111}
        >>> braid(corridor, 3, 1)
        0
    """
    if rng is None:
        rng = random.Random()
    frozen = frozenset(protected)
    dead = [
        cell
        for cell, walls in grid.items()
        if cell not in frozen and walls.bit_count() == 3
    ]
    opened = 0
    for cell in dead:
        walls = grid[cell]
        if walls.bit_count() != 3:
            continue  # an earlier opening already reached this cell
        choices: list[tuple[Direction, Cell]] = []
        for direction in Direction:
            if not walls & int(direction.value):
                continue
            drow, dcol = STEP[direction]
            neighbour = (cell[0] + drow, cell[1] + dcol)
            if not (
                0 <= neighbour[0] < height and 0 <= neighbour[1] < width
            ):
                continue  # an outer wall stays closed
            if neighbour in frozen:
                continue  # the "42" never gains a breach
            choices.append((direction, neighbour))
        if not choices:
            continue  # corridor end: no safe wall to knock down
        direction, neighbour = rng.choice(choices)
        grid[cell] &= ~int(direction.value)
        grid[neighbour] &= ~int(OPPOSITE[direction].value)
        opened += 1
    return opened


if __name__ == "__main__":
    import doctest

    raise SystemExit(1 if doctest.testmod().failed else 0)
