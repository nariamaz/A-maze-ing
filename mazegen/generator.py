"""Concrete maze carver: iterative recursive backtracker.

Why this algorithm: it guarantees a *perfect* maze (spanning tree, no
loops) in linear time, is seed-reproducible and carves one cell per
step — which makes the :meth:`MazeGenerator.steps` animation hook
trivial, thanks to the explicit stack that replaces recursion and the
``yield`` generator that drives the hook.

With ``perfect=False`` the carving is followed by the braiding pass of
:mod:`mazegen.braiding` (same random stream, no extra yields), which
knocks one wall per dead end to weave loops into the board.
"""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Optional, Tuple

from mazegen import braiding, pattern42, solver
from mazegen.api import AbstractMazeGenerator
from mazegen.constants import (
    ALL_WALLS,
    OPPOSITE,
    STEP,
    Cell,
    Direction,
)
from mazegen.errors import (
    InvalidDimensionsError,
    OutOfBoundsError,
    OverlappingEndpointsError,
    PatternCollisionError,
)


class MazeGenerator(AbstractMazeGenerator):
    """Carve a maze with an explicit-stack depth-first walk.

    Examples:
        >>> gen = MazeGenerator(15, 11, seed=42)
        >>> gen.generate()
        >>> len(gen.pattern)  # doctest: +SKIP

    Args:
        width: Number of columns (cells); must be ``>= 1``.
        height: Number of rows (cells); must be ``>= 1``.
        seed: Reproducibility seed; ``None`` gives a new maze every
            run, an equal seed repaints the exact same maze.
        perfect: ``True`` keeps one single path between any two cells;
            ``False`` braids the board (``braiding.py``).
        entry: ``(row, col)`` of the entrance cell, inside bounds;
            defaults to ``(0, 0)``.
        exit: ``(row, col)`` of the exit cell, inside bounds; defaults
            to ``(height - 1, width - 1)``.

    Raises:
        InvalidDimensionsError: When ``width`` or ``height`` is < 1.
        OutOfBoundsError: When ``entry``/``exit`` lies outside.
        OverlappingEndpointsError: When ``entry == exit``.
        PatternCollisionError: When the board could host the "42" but
            no anchor placement avoids entry and exit.
    """

    def __init__(
        self,
        width: int,
        height: int,
        seed: Optional[int] = None,
        perfect: bool = True,
        entry: Optional[Cell] = None,
        exit: Optional[Cell] = None,
    ) -> None:
        if width < 1:
            raise InvalidDimensionsError(
                f"maze width must be >= 1, got {width}"
            )
        if height < 1:
            raise InvalidDimensionsError(
                f"maze height must be >= 1, got {height}"
            )
        self.width = width
        self.height = height
        self.seed = seed
        self.perfect = perfect
        self._entry = self._check_cell("entry", entry, (0, 0))
        self._exit = self._check_cell(
            "exit", exit, (self.height - 1, self.width - 1)
        )
        if self._entry == self._exit:
            raise OverlappingEndpointsError(
                f"entry and exit are the same cell: {self._entry}"
            )
        self._pattern = self._place_pattern()
        self._grid: dict[Cell, int] = {
            (row, col): ALL_WALLS
            for row in range(self.height)
            for col in range(self.width)
        }
        self._carved = False
        self._solution: Optional[str] = None

    def _check_cell(
        self,
        name: str,
        value: Optional[Cell],
        default: Cell,
    ) -> Cell:
        """Validate one board coordinate or take the given default."""
        if value is None:
            return default
        row, col = value
        if not (0 <= row < self.height and 0 <= col < self.width):
            raise OutOfBoundsError(f"{name} outside the bounds: {value}")
        return (row, col)

    def _place_pattern(self) -> frozenset[Cell]:
        """Choose the "42" anchor, or none when the board is too small."""
        for anchor in pattern42.candidate_anchors(self.width, self.height):
            row_start, row_end, col_start, col_end = (
                pattern42.anchor_bounds(anchor)
            )
            blocked = any(
                row_start <= point[0] < row_end
                and col_start <= point[1] < col_end
                for point in (self._entry, self._exit)
            )
            if not blocked:
                return frozenset(pattern42.pattern_cells(anchor))
        if pattern42.pattern_fits(self.width, self.height):
            raise PatternCollisionError(
                "no '42' placement avoids both entry and exit; use a "
                "larger maze"
            )
        return frozenset()

    @property
    def entry(self) -> Cell:
        """The entrance cell, as a ``(row, col)`` tuple."""
        return self._entry

    @property
    def exit(self) -> Cell:
        """The exit cell, as a ``(row, col)`` tuple."""
        return self._exit

    @property
    def grid(self) -> dict[Cell, int]:
        """Wall bitmask for every cell, including the closed "42"."""
        return self._grid

    @property
    def pattern(self) -> frozenset[Cell]:
        """Closed cells of the "42"; empty when the board is small."""
        return self._pattern

    @property
    def solution(self) -> Tuple[Cell, Cell, str]:
        """The shortest route, exposed as ``(entry, exit, path)``.

        ``path`` follows the subject's output-file format (section
        IV.5): one ``N``/``E``/``S``/``W`` letter per move,
        concatenated — e.g. ``"ESENEEE"``. The BFS solver of
        ``mazegen.solver`` computes it on first access, then it is
        cached; a fresh instance (possibly reusing the same seed)
        carves and solves its own maze.

        Raises:
            RuntimeError: When the maze was not carved yet (call
                :meth:`generate` first).
        """
        if not self._carved:
            raise RuntimeError(
                "this MazeGenerator did not carve a maze yet; call "
                "generate() before asking for the solution"
            )
        if self._solution is None:
            self._solution = solver.solve(
                self._grid, self.width, self.height, self._entry,
                self._exit,
            )
        return (self._entry, self._exit, self._solution)

    def steps(self) -> Iterator[Cell]:
        """Carve the maze, yielding every carved cell in order.

        Each yield marks one newly opened passage: callers may redraw
        the current :attr:`grid` between yields to animate the carving.
        The maze is complete once the iteration ends.

        Raises:
            RuntimeError: If this instance was already generated (the
                same seed on a fresh instance repeats it exactly).

        With ``perfect=False`` the braid pass of
        :mod:`mazegen.braiding` runs after the carving loop, reusing
        this same random stream and yielding nothing extra: the maze
        is complete — and braided — once the iteration ends.
        """
        if self._carved:
            raise RuntimeError(
                "this MazeGenerator already carved its maze; create a "
                "fresh instance (optionally reusing the same seed)"
            )
        rng = random.Random(self.seed)
        current: Cell = self._entry
        visited: set[Cell] = {current}
        stack: list[Cell] = [current]
        yield current
        while stack:
            cell = stack[-1]
            options = self._carving_options(cell, visited)
            if not options:
                stack.pop()
                continue
            direction, neighbour = rng.choice(options)
            self._open_walls(cell, direction)
            visited.add(neighbour)
            stack.append(neighbour)
            yield neighbour
        expected = self.width * self.height - len(self._pattern)
        if len(visited) != expected:
            raise RuntimeError(
                "carving left unreachable cells: "
                f"{len(visited)} visited, {expected} expected"
            )
        if not self.perfect:
            braiding.braid(
                self._grid, self.width, self.height, self._pattern, rng
            )
        self._carved = True

    def generate(self) -> None:
        """Consume :meth:`steps` silently (no animation rendering)."""
        for _ in self.steps():
            pass

    def _open_walls(self, cell: Cell, direction: Direction) -> None:
        """Clear the shared wall between ``cell`` and its neighbour."""
        drow, dcol = STEP[direction]
        neighbour = (cell[0] + drow, cell[1] + dcol)
        self._grid[cell] &= ~int(direction.value)
        self._grid[neighbour] &= ~int(OPPOSITE[direction].value)

    def _carving_options(
        self,
        cell: Cell,
        visited: set[Cell],
    ) -> list[tuple[Direction, Cell]]:
        """In-bounds, closed and uncarved neighbours of ``cell``."""
        row, col = cell
        options: list[tuple[Direction, Cell]] = []
        for direction in Direction:
            drow, dcol = STEP[direction]
            neighbour = (row + drow, col + dcol)
            if (
                0 <= neighbour[0] < self.height
                and 0 <= neighbour[1] < self.width
                and neighbour not in visited
                and neighbour not in self._pattern
            ):
                options.append((direction, neighbour))
        return options
