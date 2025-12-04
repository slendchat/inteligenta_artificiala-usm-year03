from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

from . import heuristics, search, state


@dataclass
class ExperimentRow:
    algorithm: str
    search_type: str
    heuristic: str
    visited: int
    depth: int
    runtime: float
    branching: float


def run_suite() -> List[ExperimentRow]:
    configs: List[tuple[str, str, Callable[[], search.SearchResult], str]] = [
        ("Forward plain", "Forward", lambda: search.forward_search(heuristics.zero), "—"),
        ("Forward h₁", "Forward", lambda: search.forward_search(heuristics.remaining_crates), "Remaining"),
        ("Backward h₁", "Backward", lambda: search.backward_search(heuristics.start_distance), "StartDistance"),
        ("Bidirectional", "Bidirectional", search.bidirectional_search, "—"),
    ]
    rows: List[ExperimentRow] = []
    for name, search_type, fn, heuristic_name in configs:
        result = fn()
        rows.append(
            ExperimentRow(
                algorithm=name,
                search_type=search_type,
                heuristic=heuristic_name,
                visited=result.visited,
                depth=result.depth,
                runtime=result.runtime,
                branching=result.branching_factor,
            )
        )
    return rows


def estimate_branching(samples: int = 20) -> float:
    start = state.initial_state()
    frontier = [start]
    visited = {start}
    out_counts: List[int] = []
    while frontier and len(out_counts) < samples:
        node = frontier.pop(0)
        succ = state.successors(node)
        out_counts.append(len(succ))
        for tr in succ:
            if tr.target not in visited:
                visited.add(tr.target)
                frontier.append(tr.target)
    return sum(out_counts) / len(out_counts) if out_counts else 0.0


def time_vs_branching_data() -> List[tuple[float, float]]:
    rows = run_suite()
    return [(row.branching, row.runtime) for row in rows if row.branching > 0]
