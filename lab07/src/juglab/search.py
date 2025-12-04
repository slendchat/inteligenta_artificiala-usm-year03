from __future__ import annotations

import heapq
import time
from collections import deque
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from . import heuristics, state

GoalTest = Callable[[state.JugState], bool]


@dataclass
class SearchResult:
    strategy: str
    found: bool
    path: List[state.JugState]
    actions: List[str]
    explored_order: List[state.JugState]
    visited_count: int
    generated_count: int
    cost: int
    runtime: float


def _reconstruct_path(
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]],
    goal: state.JugState,
) -> Tuple[List[state.JugState], List[str]]:
    states: List[state.JugState] = []
    actions: List[str] = []
    node: Optional[state.JugState] = goal
    while node is not None:
        states.append(node)
        entry = parents[node]
        if entry is not None:
            node, action = entry
            actions.append(action)
        else:
            node = None
    states.reverse()
    actions.reverse()
    return states, actions


def _goal_checker(goals: Optional[Iterable[state.JugState]]) -> GoalTest:
    if goals is None:
        return state.JugState.is_goal
    goal_set = set(goals)
    return lambda st: st in goal_set


def breadth_first_search(
    start: state.JugState = state.INITIAL_STATE,
    goals: Optional[Iterable[state.JugState]] = None,
) -> SearchResult:
    goal_test = _goal_checker(goals)
    queue = deque([start])
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {start: None}
    explored: List[state.JugState] = []
    visited = {start}
    generated = 0
    t0 = time.perf_counter()
    while queue:
        current = queue.popleft()
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="BFS",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(visited),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        for tr in state.successors(current):
            generated += 1
            if tr.target not in visited:
                visited.add(tr.target)
                parents[tr.target] = (current, tr.action)
                queue.append(tr.target)
    dt = time.perf_counter() - t0
    return SearchResult(
        strategy="BFS",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=len(visited),
        generated_count=generated,
        cost=0,
        runtime=dt,
    )


def depth_first_search(
    start: state.JugState = state.INITIAL_STATE,
    goals: Optional[Iterable[state.JugState]] = None,
    depth_limit: Optional[int] = None,
) -> SearchResult:
    goal_test = _goal_checker(goals)
    stack: List[Tuple[state.JugState, int]] = [(start, 0)]
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {start: None}
    explored: List[state.JugState] = []
    visited = {start}
    generated = 0
    t0 = time.perf_counter()
    while stack:
        current, depth = stack.pop()
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="DFS",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(visited),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        if depth_limit is not None and depth >= depth_limit:
            continue
        for tr in reversed(state.successors(current)):
            generated += 1
            if tr.target not in visited:
                visited.add(tr.target)
                parents[tr.target] = (current, tr.action)
                stack.append((tr.target, depth + 1))
    dt = time.perf_counter() - t0
    return SearchResult(
        strategy="DFS",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=len(visited),
        generated_count=generated,
        cost=0,
        runtime=dt,
    )


def greedy_best_first_search(
    start: state.JugState = state.INITIAL_STATE,
    goals: Optional[Iterable[state.JugState]] = None,
    heuristic: heuristics.Heuristic = heuristics.difference_to_target,
) -> SearchResult:
    goal_test = _goal_checker(goals)
    frontier: List[Tuple[int, int, state.JugState]] = []
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {start: None}
    visited = {start}
    explored: List[state.JugState] = []
    generated = 0
    counter = 0
    t0 = time.perf_counter()
    heapq.heappush(frontier, (heuristic(start), counter, start))
    counter += 1
    while frontier:
        _, _, current = heapq.heappop(frontier)
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="Greedy",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(visited),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        for tr in state.successors(current):
            generated += 1
            if tr.target not in visited:
                visited.add(tr.target)
                parents[tr.target] = (current, tr.action)
                heapq.heappush(frontier, (heuristic(tr.target), counter, tr.target))
                counter += 1
    dt = time.perf_counter() - t0
    return SearchResult(
        strategy="Greedy",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=len(visited),
        generated_count=generated,
        cost=0,
        runtime=dt,
    )


def a_star_search(
    start: state.JugState = state.INITIAL_STATE,
    goals: Optional[Iterable[state.JugState]] = None,
    heuristic: heuristics.Heuristic = heuristics.difference_to_target,
) -> SearchResult:
    goal_test = _goal_checker(goals)
    frontier: List[Tuple[int, int, state.JugState]] = []
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {start: None}
    g_costs: Dict[state.JugState, int] = {start: 0}
    explored: List[state.JugState] = []
    generated = 0
    counter = 0
    t0 = time.perf_counter()
    heapq.heappush(frontier, (heuristic(start), counter, start))
    counter += 1
    while frontier:
        _, _, current = heapq.heappop(frontier)
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="A*",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(g_costs),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        for tr in state.successors(current):
            generated += 1
            tentative = g_costs[current] + tr.cost
            if tr.target not in g_costs or tentative < g_costs[tr.target]:
                g_costs[tr.target] = tentative
                parents[tr.target] = (current, tr.action)
                priority = tentative + heuristic(tr.target)
                heapq.heappush(frontier, (priority, counter, tr.target))
                counter += 1
    dt = time.perf_counter() - t0
    return SearchResult(
        strategy="A*",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=len(g_costs),
        generated_count=generated,
        cost=0,
        runtime=dt,
    )


def backward_bfs(
    goals: Iterable[state.JugState],
    target: state.JugState = state.INITIAL_STATE,
) -> SearchResult:
    pred_map = state.predecessor_map()
    goal_test = _goal_checker([target])
    queue = deque()
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {}
    visited = set()
    explored: List[state.JugState] = []
    generated = 0
    for g in goals:
        queue.append(g)
        parents[g] = None
        visited.add(g)
    t0 = time.perf_counter()
    while queue:
        current = queue.popleft()
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="Backward BFS",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(visited),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        for tr in pred_map[current]:
            generated += 1
            if tr.target not in visited:
                visited.add(tr.target)
                parents[tr.target] = (current, tr.action)
                queue.append(tr.target)
    dt = time.perf_counter() - t0
    return SearchResult(
        strategy="Backward BFS",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=len(visited),
        generated_count=generated,
        cost=0,
        runtime=dt,
    )


def mixed_strategy(
    start: state.JugState = state.INITIAL_STATE,
    goals: Optional[Iterable[state.JugState]] = None,
    bfs_depth: int = 2,
    heuristic: heuristics.Heuristic = heuristics.difference_to_target,
) -> SearchResult:
    goal_test = _goal_checker(goals)
    queue = deque([(start, 0)])
    parents: Dict[state.JugState, Optional[Tuple[state.JugState, str]]] = {start: None}
    visited = {start}
    explored: List[state.JugState] = []
    frontier: List[state.JugState] = []
    generated = 0
    t0 = time.perf_counter()

    while queue:
        current, depth = queue.popleft()
        explored.append(current)
        if goal_test(current):
            path, actions = _reconstruct_path(parents, current)
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="Mixed",
                found=True,
                path=path,
                actions=actions,
                explored_order=explored,
                visited_count=len(visited),
                generated_count=generated,
                cost=len(actions),
                runtime=dt,
            )
        if depth >= bfs_depth:
            frontier.append(current)
            continue
        for tr in state.successors(current):
            generated += 1
            if tr.target not in visited:
                visited.add(tr.target)
                parents[tr.target] = (current, tr.action)
                queue.append((tr.target, depth + 1))

    best_result: Optional[SearchResult] = None
    explored_count = len(explored)
    generated_mixed = generated
    for node in frontier:
        sub_result = greedy_best_first_search(start=node, goals=goals, heuristic=heuristic)
        generated_mixed += sub_result.generated_count
        explored_count += sub_result.visited_count
        if sub_result.found:
            path_prefix, actions_prefix = _reconstruct_path(parents, node)
            full_path = path_prefix[:-1] + sub_result.path
            full_actions = actions_prefix + sub_result.actions
            dt = time.perf_counter() - t0
            return SearchResult(
                strategy="Mixed",
                found=True,
                path=full_path,
                actions=full_actions,
                explored_order=explored + sub_result.explored_order,
                visited_count=explored_count,
                generated_count=generated_mixed,
                cost=len(full_actions),
                runtime=dt,
            )
        best_result = sub_result
    dt = time.perf_counter() - t0
    if best_result:
        explored += best_result.explored_order
    return SearchResult(
        strategy="Mixed",
        found=False,
        path=[],
        actions=[],
        explored_order=explored,
        visited_count=explored_count if frontier else len(visited),
        generated_count=generated_mixed,
        cost=0,
        runtime=dt,
    )
