"""Typed exception hierarchy of the maze engine (owner: pagente A).

Every engine failure raises a subclass of :class:`MazeError`, so `app/`
can catch one type and show a friendly message without tracebacks.

Exceptions here must stay independent of any GUI or terminal detail —
they carry plain data (messages, offending values only).
"""

from __future__ import annotations


class MazeError(Exception):
    """Base class for all engine-side failures."""


class InvalidDimensionsError(MazeError):
    """The requested ``width`` or ``height`` is impossible (< 1)."""


class OutOfBoundsError(MazeError):
    """An ``entry`` or ``exit`` coordinate lies outside the board."""


class OverlappingEndpointsError(MazeError):
    """Entrance and exit are the same cell; the maze would have
    no route."""


class PatternCollisionError(MazeError):
    """The board could host the "42", but no anchor avoids
    both ``entry`` and ``exit``."""
