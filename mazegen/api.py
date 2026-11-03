"""Public interface of the maze engine (owner: pagente A).

``AbstractMazeGenerator`` is the template every algorithm must follow.
Declaring it as an ABC (piscina PM05/PM07: abstract classes, interfaces
and the Template/Strategy design styles) lets future bonus algorithms
plug in without touching `app/`: the application layer depends only on
this shape, never on a concrete class.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Tuple

from mazegen.constants import Cell


class AbstractMazeGenerator(ABC):
    """Contract expected from any maze-carving algorithm.

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
        """``(entry, exit, path)`` with path as an ``"N...W"`` string.

        The engine fills it in Fase 2 once the BFS solver lands.
        """
        raise NotImplementedError("solver lands in Fase 2")
