from __future__ import annotations

from typing import Callable, Dict

from . import state

Heuristic = Callable[[state.JugState], int]


def difference_to_target(st: state.JugState) -> int:
    """Admissible heuristic: conservative difference scaled by jug change rate."""
    return abs(st.big - state.GOAL_VOLUME) // 2


def zero_heuristic(_: state.JugState) -> int:
    return 0


def catalog() -> Dict[str, Heuristic]:
    return {
        "zero": zero_heuristic,
        "difference": difference_to_target,
    }
