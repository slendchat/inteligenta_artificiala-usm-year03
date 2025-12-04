from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict

from . import analysis, heuristics, search, state, visualization


def _print_result(result: search.SearchResult) -> None:
    print("-" * 40)
    print(f"Strategy: {result.strategy}")
    print(f"Found: {result.found}")
    if result.found:
        print(f"Cost (steps): {result.cost}")
        print(visualization.format_path(result))
    print(f"Visited states: {result.visited_count}")
    print(f"Generated states: {result.generated_count}")
    print(f"Runtime: {result.runtime:.6f}s")
    print("-" * 40)


def _pick_heuristic() -> heuristics.Heuristic:
    options = heuristics.catalog()
    keys = list(options.keys())
    print("Available heuristics:")
    for idx, name in enumerate(keys, start=1):
        print(f"{idx}. {name}")
    choice = input("Choose heuristic (default 1): ").strip()
    try:
        idx = int(choice) - 1 if choice else 0
    except ValueError:
        idx = 0
    idx = max(0, min(idx, len(keys) - 1))
    return options[keys[idx]]


def _export_graph() -> None:
    path = input("Enter output DOT path (default: jug_graph.dot): ").strip() or "jug_graph.dot"
    out = visualization.export_graphviz(path)
    print(f"Graph exported to {out.resolve()}")


def _validate_heuristic() -> None:
    heuristic = _pick_heuristic()
    report = analysis.evaluate_heuristic(heuristic)
    print(f"Heuristic admissible: {report['admissible']}")
    print(f"Heuristic consistent: {report['consistent']}")


def run_ui() -> None:
    default_goals = list(state.goal_states())
    heuristic = heuristics.difference_to_target

    def _set_heuristic() -> None:
        nonlocal heuristic
        heuristic = _pick_heuristic()
        print("Selected new heuristic.")

    actions: Dict[str, Callable[[], None]] = {
        "1": lambda: _print_result(search.breadth_first_search(goals=default_goals)),
        "2": lambda: _print_result(
            search.depth_first_search(goals=default_goals, depth_limit=10)
        ),
        "3": lambda: _print_result(
            search.a_star_search(goals=default_goals, heuristic=heuristic)
        ),
        "4": lambda: _print_result(
            search.greedy_best_first_search(goals=default_goals, heuristic=heuristic)
        ),
        "5": lambda: _print_result(
            search.backward_bfs(goals=default_goals)
        ),
        "6": lambda: _print_result(
            search.mixed_strategy(goals=default_goals, heuristic=heuristic)
        ),
        "7": lambda: print(
            analysis.format_results_table(analysis.run_strategy_suite())
        ),
        "8": _export_graph,
        "9": _validate_heuristic,
        "10": _set_heuristic,
    }

    while True:
        print(
            "\nJug Solver UI\n"
            "1. Breadth-first search\n"
            "2. Depth-first search\n"
            "3. A* search\n"
            "4. Greedy search\n"
            "5. Backward BFS\n"
            "6. Mixed strategy\n"
            "7. Compare strategies\n"
            "8. Export state graph (DOT)\n"
            "9. Validate heuristic\n"
            "10. Switch heuristic\n"
            "0. Exit\n"
        )
        choice = input("Select option: ").strip()
        if choice == "0":
            print("Goodbye.")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid selection.")


def main() -> None:
    run_ui()


if __name__ == "__main__":
    main()
