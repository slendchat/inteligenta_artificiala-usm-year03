from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from planner import experiments, heuristics, search, state

CELL_SIZE = 30
PADDING = 10


class PlannerApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Lab 08 — Planning Directions")
        self.resizable(False, False)
        self.configure(bg="#f5f6fa")
        self._create_widgets()
        self._draw_static_board()
        self.animation_states: list[state.State] = []
        self.animation_index = 0

    def _create_widgets(self) -> None:
        main = ttk.Frame(self, padding=10)
        main.grid(row=0, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            main,
            width=state.GRID_WIDTH * CELL_SIZE + 2 * PADDING,
            height=state.GRID_HEIGHT * CELL_SIZE + 2 * PADDING,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 10))

        control_frame = ttk.Frame(main, padding=10)
        control_frame.grid(row=0, column=1, sticky="nsew")

        ttk.Label(control_frame, text="Search mode:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar(value="Forward (plain)")
        search_options = [
            "Forward (plain)",
            "Forward (Remaining)",
            "Forward (Distance)",
            "Backward (StartDistance)",
            "Bidirectional",
        ]
        ttk.OptionMenu(control_frame, self.search_var, search_options[0], *search_options).grid(
            row=1, column=0, sticky="ew", pady=(0, 10)
        )

        ttk.Button(control_frame, text="Run search", command=self.run_selected_search).grid(
            row=2, column=0, sticky="ew"
        )

        ttk.Separator(control_frame, orient="horizontal").grid(
            row=3, column=0, sticky="ew", pady=10
        )

        self.metrics_text = tk.StringVar(value="Metrics will appear here.")
        ttk.Label(control_frame, textvariable=self.metrics_text, justify="left").grid(
            row=4, column=0, sticky="w"
        )

        ttk.Button(control_frame, text="Run experiment suite", command=self.populate_table).grid(
            row=5, column=0, sticky="ew", pady=(10, 0)
        )

        table_frame = ttk.Frame(main)
        table_frame.grid(row=1, column=1, sticky="nsew")
        columns = ("algorithm", "heuristic", "visited", "depth", "time")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        headings = {
            "algorithm": "Algorithm",
            "heuristic": "Heuristic",
            "visited": "Visited",
            "depth": "Depth",
            "time": "Time (s)",
        }
        for col, label in headings.items():
            self.table.heading(col, text=label)
            self.table.column(col, anchor="center", width=110)
        self.table.grid(row=0, column=0, sticky="nsew")
        ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview).grid(
            row=0, column=1, sticky="ns"
        )
        self.table.configure(yscrollcommand=lambda *args: None)

        chart_frame = ttk.Frame(main, padding=(0, 10, 0, 0))
        chart_frame.grid(row=2, column=1, sticky="nsew")
        ttk.Label(chart_frame, text="Время vs коэффициент ветвления").grid(
            row=0, column=0, sticky="w"
        )
        self.chart_canvas = tk.Canvas(chart_frame, width=320, height=160, bg="white")
        self.chart_canvas.grid(row=1, column=0)

    def _draw_static_board(self) -> None:
        self.canvas.delete("all")
        for x in range(state.GRID_WIDTH):
            for y in range(state.GRID_HEIGHT):
                left = PADDING + x * CELL_SIZE
                top = PADDING + y * CELL_SIZE
                color = "#f0f0f0"
                if (x, y) in state.OBSTACLES:
                    color = "#b0bec5"
                if (x, y) == state.BASE:
                    color = "#ffe082"
                self.canvas.create_rectangle(
                    left,
                    top,
                    left + CELL_SIZE,
                    top + CELL_SIZE,
                    fill=color,
                    outline="#d0d0d0",
                )
        for idx, crate in enumerate(state.CRATES):
            self._draw_crate(crate, delivered=False, tag=f"crate{idx}")
        self._draw_agent(state.initial_state(), tag="agent")

    def _draw_crate(self, pos: state.Position, delivered: bool, tag: str) -> None:
        self.canvas.delete(tag)
        x, y = pos
        left = PADDING + x * CELL_SIZE + CELL_SIZE * 0.2
        top = PADDING + y * CELL_SIZE + CELL_SIZE * 0.2
        color = "#66bb6a" if not delivered else "#aed581"
        self.canvas.create_rectangle(
            left,
            top,
            left + CELL_SIZE * 0.6,
            top + CELL_SIZE * 0.6,
            fill=color,
            outline="",
            tags=tag,
        )

    def _draw_agent(self, st: state.State, tag: str = "agent") -> None:
        self.canvas.delete(tag)
        x, y = st.agent
        left = PADDING + x * CELL_SIZE + CELL_SIZE * 0.15
        top = PADDING + y * CELL_SIZE + CELL_SIZE * 0.15
        color = "#42a5f5" if st.carrying is None else "#ef5350"
        self.canvas.create_oval(
            left,
            top,
            left + CELL_SIZE * 0.7,
            top + CELL_SIZE * 0.7,
            fill=color,
            outline="white",
            width=2,
            tags=tag,
        )

    def run_selected_search(self) -> None:
        choice = self.search_var.get()
        if choice == "Forward (plain)":
            result = search.forward_search(heuristics.zero)
        elif choice == "Forward (Remaining)":
            result = search.forward_search(heuristics.remaining_crates)
        elif choice == "Forward (Distance)":
            result = search.forward_search(heuristics.distance_based)
        elif choice == "Backward (StartDistance)":
            result = search.backward_search(heuristics.start_distance)
        else:
            result = search.bidirectional_search()
        if result.found:
            self.metrics_text.set(
                f"{result.name} found solution\n"
                f"Depth: {result.depth}\n"
                f"Visited: {result.visited}\n"
                f"Generated: {result.generated}\n"
                f"Runtime: {result.runtime:.4f}s\n"
                f"Branching: {result.branching_factor:.2f}"
            )
            self.animation_states = result.path
            self.animation_index = 0
            self.after(100, self._animate_step)
        else:
            self.metrics_text.set(f"{result.name}: solution not found.")

    def _animate_step(self) -> None:
        if self.animation_index >= len(self.animation_states):
            return
        current_state = self.animation_states[self.animation_index]
        for idx, crate_pos in enumerate(state.CRATES):
            delivered = current_state.delivered[idx]
            self._draw_crate(crate_pos, delivered, f"crate{idx}")
        self._draw_agent(current_state)
        self.animation_index += 1
        if self.animation_index < len(self.animation_states):
            self.after(100, self._animate_step)

    def populate_table(self) -> None:
        for row in self.table.get_children():
            self.table.delete(row)
        rows = experiments.run_suite()
        for row in rows:
            self.table.insert(
                "",
                "end",
                values=(
                    row.algorithm,
                    row.heuristic,
                    row.visited,
                    row.depth,
                    f"{row.runtime:.4f}",
                ),
            )
        self._plot_time_vs_branching(rows)
        avg_branch = experiments.estimate_branching()
        self.metrics_text.set(f"Средний коэффициент ветвления ≈ {avg_branch:.2f}")

    def _plot_time_vs_branching(self, rows: list[experiments.ExperimentRow]) -> None:
        self.chart_canvas.delete("all")
        if not rows:
            return
        max_branch = max((row.branching for row in rows), default=1.0)
        max_time = max((row.runtime for row in rows), default=1.0)
        padding = 20
        width = int(self.chart_canvas["width"])
        height = int(self.chart_canvas["height"])
        self.chart_canvas.create_line(
            padding, height - padding, width - padding, height - padding, arrow=tk.LAST
        )
        self.chart_canvas.create_line(
            padding, height - padding, padding, padding, arrow=tk.LAST
        )
        for row in rows:
            if row.branching == 0:
                continue
            x = padding + (row.branching / max_branch) * (width - 2 * padding)
            y = height - padding - (row.runtime / max_time) * (height - 2 * padding)
            self.chart_canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="#ef5350")
            self.chart_canvas.create_text(x + 5, y - 5, text=row.search_type, anchor="w", font=("Arial", 8))


def main() -> None:
    app = PlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
