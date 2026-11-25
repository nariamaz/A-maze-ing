"""Public interface of the maze engine.

``AbstractMazeGenerator`` is the template every algorithm must follow.
Declaring it as an ABC lets future bonus algorithms plug in without
touching `app/`: the application layer depends only on this shape,
never on a concrete class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Tuple, Any

from mazegen.constants import Cell


class AbstractMazeGenerator(ABC):
    """Interface expected from any maze-carving algorithm.

    Subclasses promise:

    * ``generate()`` — carve the whole maze synchronously (no render).
    * ``steps()`` — animation hook: one ``Cell`` yielded per carving
      step; the maze is complete when the iterator is exhausted.
    * ``grid`` — read-only mapping ``Cell -> wall bitmask`` for every
      cell, including the fully closed ones.
    * ``pattern`` — the closed cells of the "42" (empty when the board
      is too small to host it).

    The concrete ``MazeGenerator`` (recursive-backtracker style, born
    in ``generator.py``) is the first implementation.
    """

    @abstractmethod
    def generate(self) -> None:
        """Carve the entire maze synchronously."""

    @abstractmethod
    def steps(self) -> Iterator[Cell]:
        """Carve the maze, yielding every carved cell in order."""

    @property
    @abstractmethod
    def grid(self) -> dict[Cell, int]:
        """Wall bitmask for every cell; ``(row, col) -> int``."""

    @property
    @abstractmethod
    def pattern(self) -> frozenset[Cell]:
        """Closed cells of the "42"; empty when it does not fit."""

    @property
    def solution(self) -> Tuple[Cell, Cell, str]:
        """``(entry, exit, path)`` once the maze is carved.

        ``path`` follows the output file of the subject (section
        IV.5): one ``N``/``E``/``S``/``W`` letter per move,
        concatenated. Concrete carvers implement it on top of
        ``mazegen.solver.solve``.
        """
        raise NotImplementedError("the concrete carver provides it")
