from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from . import search, state


def _label(st: state.JugState) -> str:
    return f"{st.big}L_{st.small}L"


def export_graphviz(path: str | Path) -> Path:
    path = Path(path)
    nodes, edges = state.build_full_state_graph()
    lines = ["digraph Jugs {", "  rankdir=LR;"]
    for node in nodes:
        style = ' shape=doublecircle' if node.is_goal() else ""
        lines.append(f'  "{_label(node)}" [label="{node.big},{node.small}"{style}];')
    for tr in edges:
        lines.append(
            f'  "{_label(tr.source)}" -> "{_label(tr.target)}" [label="{tr.action}"];'
        )
    lines.append("}")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def format_path(result: search.SearchResult) -> str:
    if not result.found:
        return f"{result.strategy}: No solution"
    parts: List[str] = []
    for idx, st in enumerate(result.path):
        prefix = "Start" if idx == 0 else f"Step {idx}"
        parts.append(f"{prefix}: ({st.big}, {st.small})")
        if idx < len(result.actions):
            parts.append(f"  └─ {result.actions[idx]}")
    return "\n".join(parts)


def format_sequence(states: Iterable[state.JugState]) -> str:
    return " -> ".join(f"({s.big},{s.small})" for s in states)
