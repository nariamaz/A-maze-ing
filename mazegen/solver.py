"""BFS shortest-path solver (owner: pagente A).

The subject asks the output file to carry the shortest valid path from
entry to exit (section IV.5: entry coordinates, exit coordinates and
the path written with the four letters ``N``, ``E``, ``S``, ``W``).
Breadth-first search fits: the maze graph is unweighted, so the route
found when the exit is first reached is a shortest one — and on a
perfect maze the route is unique anyway.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Mapping

from mazegen.constants import ALL_WALLS, OPPOSITE, STEP, Cell, Direction
from mazegen.errors import NoSolutionError

_LETTERS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}
"""Subject IV.5 letter of each direction, one character per move."""


def solve(
    grid: Mapping[Cell, int],
    width: int,
    height: int,
    entry: Cell,
    exit: Cell,
) -> str:
    """Find the shortest ``entry``->``exit`` route over open passages.

    A passage is open only when both adjacent cells agree (closed-wall
    bit clear on both sides — the wall-coherence rule of the subject).
    A cell missing from *grid* counts as fully closed, which keeps the
    isolated "42" cells unreachable. Neighbours are tried in the fixed
    ``N, E, S, W`` order, so the same grid always yields the same
    string (seed-reproducibility friendly).

    Args:
        grid: Wall bitmask ``Cell -> int`` (``N = 1, E = 2, S = 4,
            W = 8``; a set bit is a closed wall).
        width: Number of columns of the board.
        height: Number of rows of the board.
        entry: Starting cell, as ``(row, col)``.
        exit: Target cell, as ``(row, col)``; must differ from *entry*.

    Returns:
        The shortest path as concatenated letters, e.g. ``"ESENEEE"`` —
        exactly what `app/` writes in the output file footer.

    Raises:
        NoSolutionError: When *entry* and *exit* are the same cell,
            lie outside the ``width`` x ``height`` board, or when no
            open route connects them.

    Examples:
        A 1x2 board whose single open wall links both cells:

        >>> solve({(0, 0): 0b1101, (0, 1): 0b0111}, 2, 1, (0, 0), (0, 1))
        'E'

        A 3x1 corridor with no forks: the route is simply East twice.

        >>> solve(
        ...     {(0, 0): 0b1101, (0, 1): 0b0101, (0, 2): 0b0111},
        ...     3, 1, (0, 0), (0, 2),
        ... )
        'EE'
    """
    if entry == exit:
        raise NoSolutionError(f"entry and exit are the same cell: {entry}")
    for point in (entry, exit):
        if not (0 <= point[0] < height and 0 <= point[1] < width):
            raise NoSolutionError(
                f"cell outside the {width}x{height} board: {point}"
            )
    parents: dict[Cell, tuple[Cell, Direction]] = {}
    seen: set[Cell] = {entry}
    queue: deque[Cell] = deque([entry])
    while queue:
        cell = queue.popleft()
        walls = grid.get(cell, ALL_WALLS)
        row, col = cell
        for direction in Direction:
            if walls & int(direction.value):
                continue
            drow, dcol = STEP[direction]
            neighbour = (row + drow, col + dcol)
            if not (0 <= neighbour[0] < height and 0 <= neighbour[1] < width):
                continue
            if grid.get(neighbour, ALL_WALLS) & int(
                OPPOSITE[direction].value
            ):
                continue
            if neighbour in seen:
                continue
            seen.add(neighbour)
            parents[neighbour] = (cell, direction)
            if neighbour == exit:
                return _trace(entry, exit, parents)
            queue.append(neighbour)
    raise NoSolutionError(f"no open route from {entry} to {exit}")


def _trace(
    entry: Cell,
    exit: Cell,
    parents: dict[Cell, tuple[Cell, Direction]],
) -> str:
    """Walk the parents backwards from *exit*, lettering each move."""
    letters: list[str] = []
    cell = exit
    while cell != entry:
        parent, direction = parents[cell]
        letters.append(_LETTERS[direction])
        cell = parent
    letters.reverse()
    return "".join(letters)


if __name__ == "__main__":
    import doctest

    raise SystemExit(1 if doctest.testmod().failed else 0)
