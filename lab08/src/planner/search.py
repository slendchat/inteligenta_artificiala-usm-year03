from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from . import heuristics, state


@dataclass
class SearchResult:
    name: str
    found: bool
    path: List[state.State]
    actions: List[str]
    visited: int
    generated: int
    runtime: float

    @property
    def depth(self) -> int:
        return max(len(self.path) - 1, 0)

    @property
    def branching_factor(self) -> float:
        return self.generated / self.visited if self.visited else 0.0


def _reconstruct(parents: Dict[state.State, Optional[Tuple[state.State, str]]], node: state.State) -> Tuple[List[state.State], List[str]]:
    states_path: List[state.State] = []
    actions: List[str] = []
    while node in parents and parents[node] is not None:
        prev, act = parents[node]
        states_path.append(node)
        actions.append(act)
        node = prev
    states_path.append(node)
    states_path.reverse()
    actions.reverse()
    return states_path, actions


def _uniform_cost_search(
    start_nodes: Iterable[state.State],
    goal_test,
    successor_fn,
    heuristic: heuristics.Heuristic,
    label: str,
    reverse_result: bool = False,
) -> SearchResult:
    t0 = time.perf_counter()
    parents: Dict[state.State, Optional[Tuple[state.State, str]]] = {}
    g_costs: Dict[state.State, int] = {}
    pq: List[Tuple[int, int, state.State]] = []
    counter = 0

    for start in start_nodes:
        parents[start] = None
        g_costs[start] = 0
        heapq.heappush(pq, (heuristic(start), counter, start))
        counter += 1

    visited = 0
    generated = 0

    while pq:
        _, _, current = heapq.heappop(pq)
        cost_so_far = g_costs[current]
        visited += 1
        if goal_test(current):
            path, actions = _reconstruct(parents, current)
            if reverse_result:
                path = list(reversed(path))
                actions = list(reversed(actions))
            runtime = time.perf_counter() - t0
            return SearchResult(
                name=label,
                found=True,
                path=path,
                actions=actions,
                visited=visited,
                generated=generated,
                runtime=runtime,
            )
        for tr in successor_fn(current):
            generated += 1
            next_cost = cost_so_far + tr.cost
            if tr.target not in g_costs or next_cost < g_costs[tr.target]:
                g_costs[tr.target] = next_cost
                parents[tr.target] = (current, tr.action)
                priority = next_cost + heuristic(tr.target)
                heapq.heappush(pq, (priority, counter, tr.target))
                counter += 1
    runtime = time.perf_counter() - t0
    return SearchResult(
        name=label,
        found=False,
        path=[],
        actions=[],
        visited=visited,
        generated=generated,
        runtime=runtime,
    )


def forward_search(heuristic: heuristics.Heuristic = heuristics.zero) -> SearchResult:
    start = state.initial_state()
    return _uniform_cost_search(
        start_nodes=[start],
        goal_test=state.State.is_goal,
        successor_fn=state.successors,
        heuristic=heuristic,
        label="Forward",
    )


def backward_search(heuristic: heuristics.Heuristic = heuristics.zero) -> SearchResult:
    target = state.initial_state()
    return _uniform_cost_search(
        start_nodes=list(state.goal_states()),
        goal_test=lambda s: s == target,
        successor_fn=state.predecessor_states,
        heuristic=heuristic,
        label="Backward",
        reverse_result=True,
    )


def bidirectional_search() -> SearchResult:
    start = state.initial_state()
    goal = state.canonical_goal_state()
    front_parents: Dict[state.State, Optional[Tuple[state.State, str]]] = {start: None}
    back_parents: Dict[state.State, Optional[Tuple[state.State, str]]] = {goal: None}
    front_queue = deque([start])
    back_queue = deque([goal])
    visited = 0
    generated = 0
    t0 = time.perf_counter()

    def _merge(meeting: state.State) -> Tuple[List[state.State], List[str]]:
        path_forward, actions_forward = _reconstruct(front_parents, meeting)
        path_backward, actions_backward = _reconstruct(back_parents, meeting)
        backward_tail = list(reversed(path_backward))[1:]
        full_path = path_forward + backward_tail
        full_actions = actions_forward + list(reversed(actions_backward))
        return full_path, full_actions

    while front_queue and back_queue:
        current_front = front_queue.popleft()
        visited += 1
        if current_front in back_parents:
            path, actions = _merge(current_front)
            runtime = time.perf_counter() - t0
            return SearchResult(
                name="Bidirectional",
                found=True,
                path=path,
                actions=actions,
                visited=visited,
                generated=generated,
                runtime=runtime,
            )
        for tr in state.successors(current_front):
            generated += 1
            if tr.target not in front_parents:
                front_parents[tr.target] = (current_front, tr.action)
                front_queue.append(tr.target)

        current_back = back_queue.popleft()
        visited += 1
        if current_back in front_parents:
            path, actions = _merge(current_back)
            runtime = time.perf_counter() - t0
            return SearchResult(
                name="Bidirectional",
                found=True,
                path=path,
                actions=actions,
                visited=visited,
                generated=generated,
                runtime=runtime,
            )
        for tr in state.predecessor_states(current_back):
            generated += 1
            if tr.target not in back_parents:
                back_parents[tr.target] = (current_back, tr.action)
                back_queue.append(tr.target)

    runtime = time.perf_counter() - t0
    return SearchResult(
        name="Bidirectional",
        found=False,
        path=[],
        actions=[],
        visited=visited,
        generated=generated,
        runtime=runtime,
    )
