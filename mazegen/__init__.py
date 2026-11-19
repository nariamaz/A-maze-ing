"""maze generation engine.

Reusable, import-free-of-app package: modules here build and query maze
data only; anything touching files or terminals belongs to the `app/`
layer.
"""

from __future__ import annotations

from mazegen.api import AbstractMazeGenerator
from mazegen.braiding import braid
from mazegen.constants import ALL_WALLS, Cell, Direction
from mazegen.errors import MazeError, NoSolutionError
from mazegen.generator import MazeGenerator
from mazegen.pattern42 import pattern_cells, pattern_fits
from mazegen.solver import solve

__all__ = [
    "ALL_WALLS",
    "AbstractMazeGenerator",
    "Cell",
    "Direction",
    "MazeError",
    "MazeGenerator",
    "NoSolutionError",
    "braid",
    "pattern_cells",
    "pattern_fits",
    "solve",
    "__version__",
]

__version__ = "1.0.0"
