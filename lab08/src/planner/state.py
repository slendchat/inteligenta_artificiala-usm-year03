from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

GRID_WIDTH = 15
GRID_HEIGHT = 15
BASE = (0, 0)
CRATES = [(12, 13), (7, 5), (3, 10)]
OBSTACLES = {
    (2, 2),
    (3, 2),
    (4, 2),
    (5, 5),
    (6, 5),
    (8, 5),
    (6, 9),
    (7, 9),
    (8, 9),
    (9, 9),
    (10, 9),
    (11, 9),
    (6, 10),
    (6, 11),
    (4, 11),
    (5, 11),
    (10, 3),
    (11, 3),
    (12, 3),
    (9, 4),
}
START_POS = (0, 14)


Position = Tuple[int, int]


@dataclass(frozen=True)
class State:
    agent: Position
    carrying: Optional[int]
    delivered: Tuple[bool, ...]

    def is_goal(self) -> bool:
        return all(self.delivered)


@dataclass(frozen=True)
class Transition:
    action: str
    source: State
    target: State
    cost: int = 1


def initial_state() -> State:
    return State(agent=START_POS, carrying=None, delivered=tuple(False for _ in CRATES))


def goal_states() -> Iterable[State]:
    delivered = tuple(True for _ in CRATES)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            pos = (x, y)
            if not is_obstacle(pos):
                yield State(agent=pos, carrying=None, delivered=delivered)


def canonical_goal_state() -> State:
    delivered = tuple(True for _ in CRATES)
    return State(agent=BASE, carrying=None, delivered=delivered)


def in_bounds(pos: Position) -> bool:
    x, y = pos
    return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT


def is_obstacle(pos: Position) -> bool:
    return pos in OBSTACLES


def move(position: Position, direction: str) -> Position:
    x, y = position
    if direction == "N":
        return x, y - 1
    if direction == "S":
        return x, y + 1
    if direction == "E":
        return x + 1, y
    if direction == "W":
        return x - 1, y
    raise ValueError(f"Unknown direction {direction}")


DIRECTIONS = ("N", "S", "E", "W")
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def successors(state: State) -> List[Transition]:
    moves: List[Transition] = []
    x, y = state.agent
    for direction in DIRECTIONS:
        nxt = move((x, y), direction)
        if in_bounds(nxt) and not is_obstacle(nxt):
            moves.append(
                Transition(
                    action=f"Move {direction}",
                    source=state,
                    target=State(agent=nxt, carrying=state.carrying, delivered=state.delivered),
                )
            )
    # pick up crate
    if state.carrying is None:
        for idx, crate_pos in enumerate(CRATES):
            if not state.delivered[idx] and crate_pos == state.agent:
                moves.append(
                    Transition(
                        action=f"Pick crate {idx}",
                        source=state,
                        target=State(agent=state.agent, carrying=idx, delivered=state.delivered),
                    )
                )
    # drop crate at base
    if state.carrying is not None and state.agent == BASE:
        delivered = list(state.delivered)
        delivered[state.carrying] = True
        moves.append(
            Transition(
                action=f"Drop crate {state.carrying}",
                source=state,
                target=State(agent=state.agent, carrying=None, delivered=tuple(delivered)),
            )
        )
    return moves


def predecessor_states(state: State) -> Iterable[Transition]:
    # reverse transitions for backward reasoning
    transitions: List[Transition] = []
    # reverse drops -> pick up at base
    if state.agent == BASE and state.carrying is None:
        for idx in range(len(CRATES)):
            if state.delivered[idx]:
                prev_delivered = list(state.delivered)
                prev_delivered[idx] = False
                prev_state = State(agent=state.agent, carrying=idx, delivered=tuple(prev_delivered))
                transitions.append(
                    Transition(
                        action=f"Drop crate {idx}",
                        source=state,
                        target=prev_state,
                    )
                )
    # reverse picks -> place crate at original location
    for idx, crate_pos in enumerate(CRATES):
        if state.carrying == idx and state.agent == crate_pos:
            prev_state = State(agent=crate_pos, carrying=None, delivered=state.delivered)
            transitions.append(
                Transition(
                    action=f"Pick crate {idx}",
                    source=state,
                    target=prev_state,
                )
            )
    # reverse moves
    for direction in DIRECTIONS:
        nxt = move(state.agent, direction)
        if in_bounds(nxt) and not is_obstacle(nxt):
            transitions.append(
                Transition(
                    action=f"Move {OPPOSITE[direction]}",
                    source=state,
                    target=State(agent=nxt, carrying=state.carrying, delivered=state.delivered),
                )
            )
    return transitions
