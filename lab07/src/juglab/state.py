from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple

CAP_BIG = 4
CAP_SMALL = 3
GOAL_VOLUME = 2


@dataclass(frozen=True)
class JugState:
    """State representing liters in the 4L (big) and 3L (small) jugs."""

    big: int
    small: int

    def __post_init__(self) -> None:
        if not (0 <= self.big <= CAP_BIG and 0 <= self.small <= CAP_SMALL):
            raise ValueError(f"Invalid jug volumes: {self}")

    def is_goal(self) -> bool:
        return self.big == GOAL_VOLUME


@dataclass(frozen=True)
class Transition:
    action: str
    source: JugState
    target: JugState
    cost: int = 1


INITIAL_STATE = JugState(0, 0)


def all_states() -> Iterable[JugState]:
    for big in range(CAP_BIG + 1):
        for small in range(CAP_SMALL + 1):
            yield JugState(big, small)


def goal_states() -> Iterable[JugState]:
    for s in range(CAP_SMALL + 1):
        yield JugState(GOAL_VOLUME, s)


def successors(state: JugState) -> List[Transition]:
    transitions: List[Transition] = []
    x, y = state.big, state.small

    def add(new_state: Tuple[int, int], action: str) -> None:
        nxt = JugState(*new_state)
        if nxt != state:
            transitions.append(Transition(action=action, source=state, target=nxt))

    if x < CAP_BIG:
        add((CAP_BIG, y), "Fill 4L jug")
    if y < CAP_SMALL:
        add((x, CAP_SMALL), "Fill 3L jug")
    if x > 0:
        add((0, y), "Empty 4L jug")
    if y > 0:
        add((x, 0), "Empty 3L jug")

    if x > 0 and y < CAP_SMALL:
        transfer = min(x, CAP_SMALL - y)
        add((x - transfer, y + transfer), "Pour 4L → 3L")
    if y > 0 and x < CAP_BIG:
        transfer = min(y, CAP_BIG - x)
        add((x + transfer, y - transfer), "Pour 3L → 4L")

    return transitions


def build_full_state_graph() -> Tuple[List[JugState], List[Transition]]:
    nodes = list(all_states())
    edges: List[Transition] = []
    for node in nodes:
        edges.extend(successors(node))
    return nodes, edges


def predecessor_map() -> Dict[JugState, List[Transition]]:
    nodes, edges = build_full_state_graph()
    mapping: Dict[JugState, List[Transition]] = {node: [] for node in nodes}
    for tr in edges:
        reverse = Transition(
            action=f"Reverse {tr.action}",
            source=tr.target,
            target=tr.source,
            cost=tr.cost,
        )
        mapping[reverse.source].append(reverse)
    return mapping
