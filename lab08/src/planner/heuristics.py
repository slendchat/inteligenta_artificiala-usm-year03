from __future__ import annotations

from typing import Callable, Dict

from . import state

Heuristic = Callable[[state.State], int]


def remaining_crates(st: state.State) -> int:
    count = sum(1 for delivered in st.delivered if not delivered)
    if st.carrying is not None and st.agent != state.BASE:
        count += 1
    return count


def distance_based(st: state.State) -> int:
    def manhattan(a: state.Position, b: state.Position) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    total = 0
    if st.carrying is not None:
        total += manhattan(st.agent, state.BASE)
        remaining = [idx for idx, done in enumerate(st.delivered) if not done and idx != st.carrying]
    else:
        remaining = [idx for idx, done in enumerate(st.delivered) if not done]
        if remaining:
            dists = [manhattan(st.agent, state.CRATES[idx]) for idx in remaining]
            total += min(dists)
    for idx in remaining:
        total += manhattan(state.CRATES[idx], state.BASE)
    return total


def zero(_: state.State) -> int:
    return 0


def start_distance(st: state.State) -> int:
    ax, ay = st.agent
    sx, sy = state.START_POS
    return abs(ax - sx) + abs(ay - sy)


def catalog() -> Dict[str, Heuristic]:
    return {
        "None": zero,
        "Remaining": remaining_crates,
        "Distance": distance_based,
        "StartDistance": start_distance,
    }
