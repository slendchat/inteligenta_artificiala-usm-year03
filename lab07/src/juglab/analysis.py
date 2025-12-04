from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List

from . import heuristics, search, state


def compute_distances_to_goal(goals: Iterable[state.JugState]) -> Dict[state.JugState, int]:
    pred = state.predecessor_map()
    queue = deque()
    distances: Dict[state.JugState, int] = {}
    for g in goals:
        queue.append((g, 0))
        distances[g] = 0
    while queue:
        node, dist = queue.popleft()
        for tr in pred[node]:
            if tr.target not in distances:
                distances[tr.target] = dist + tr.cost
                queue.append((tr.target, dist + tr.cost))
    return distances


def evaluate_heuristic(h: heuristics.Heuristic) -> Dict[str, object]:
    goals = list(state.goal_states())
    distances = compute_distances_to_goal(goals)
    admissible = True
    consistent = True
    for node, optimal in distances.items():
        if h(node) > optimal:
            admissible = False
        for tr in state.successors(node):
            if h(node) > tr.cost + h(tr.target):
                consistent = False
    return {"admissible": admissible, "consistent": consistent}


def run_strategy_suite() -> List[search.SearchResult]:
    default_goals = list(state.goal_states())
    heuristic = heuristics.difference_to_target
    return [
        search.depth_first_search(depth_limit=10, goals=default_goals),
        search.breadth_first_search(goals=default_goals),
        search.greedy_best_first_search(goals=default_goals, heuristic=heuristic),
        search.a_star_search(goals=default_goals, heuristic=heuristic),
        search.backward_bfs(goals=default_goals),
        search.mixed_strategy(goals=default_goals, heuristic=heuristic),
    ]


def format_results_table(results: List[search.SearchResult]) -> str:
    headers = [
        "Strategy",
        "Found",
        "Cost",
        "Visited",
        "Generated",
        "Runtime(s)",
    ]
    rows = []
    for res in results:
        rows.append(
            [
                res.strategy,
                "yes" if res.found else "no",
                str(res.cost),
                str(res.visited_count),
                str(res.generated_count),
                f"{res.runtime:.6f}",
            ]
        )
    widths = [max(len(row[i]) for row in [headers] + rows) for i in range(len(headers))]
    lines = []
    header_line = " | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))
    sep = "-+-".join("-" * widths[i] for i in range(len(headers)))
    lines.append(header_line)
    lines.append(sep)
    for row in rows:
        lines.append(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
    return "\n".join(lines)
