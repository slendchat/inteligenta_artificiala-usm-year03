import tkinter as tk
from tkinter import *
from tkinter import ttk


def triangle(x: float, a: float, b: float, c: float) -> float:
    if a == b == c:
        return 0.0
    if x <= a or x >= c:
        return 0.0
    if a < x < b:
        return (x - a) / (b - a)
    if b < x < c:
        return (c - x) / (c - b)
    if x == b:
        return 1.0
    return 0.0


def trapezoid(x: float, a: float, b: float, c: float, d: float) -> float:
    if x <= a or x >= d:
        return 0.0
    if b <= x <= c:
        return 1.0
    if a < x < b:
        return (x - a) / (b - a)
    if c < x < d:
        return (d - x) / (d - c)
    return 0.0


def clamp01(x: float) -> float:
    return max(0.0, min(100.0, x))


def fuzzify_demand(x: float) -> dict:
    x = clamp01(x)
    return {
        "low": trapezoid(x, 0, 0, 25, 45),
        "medium": triangle(x, 30, 50, 70),
        "high": trapezoid(x, 55, 75, 100, 100),
    }


def fuzzify_supply(x: float) -> dict:
    x = clamp01(x)
    return {
        "low": trapezoid(x, 0, 0, 25, 45),
        "normal": triangle(x, 30, 50, 70),
        "high": trapezoid(x, 55, 75, 100, 100),
    }


def fuzzify_inflation(x: float) -> dict:
    x = clamp01(x)
    return {
        "low": trapezoid(x, 0, 0, 20, 40),
        "medium": triangle(x, 30, 50, 70),
        "high": trapezoid(x, 60, 80, 100, 100),
    }


def mu_decrease(y: float) -> float:
    return trapezoid(y, 0, 0, 15, 35)


def mu_stable(y: float) -> float:
    return triangle(y, 30, 50, 70)


def mu_increase(y: float) -> float:
    return trapezoid(y, 65, 85, 100, 100)


def predict_energy_price_growth(demand_value: float, supply_value: float, inflation_value: float) -> float:
    d = fuzzify_demand(demand_value)
    s = fuzzify_supply(supply_value)
    i = fuzzify_inflation(inflation_value)

    base = {
        ("low", "high"): "decrease",
        ("low", "normal"): "decrease",
        ("low", "low"): "stable",
        ("medium", "high"): "decrease",
        ("medium", "normal"): "stable",
        ("medium", "low"): "increase",
        ("high", "high"): "stable",
        ("high", "normal"): "increase",
        ("high", "low"): "increase",
    }

    def rule_output(d_term: str, s_term: str, i_term: str) -> str:
        cons = base[(d_term, s_term)]
        if i_term == "high":
            return "increase"
        if i_term == "medium":
            return cons
        if cons == "increase":
            return "stable"
        return cons

    w = {"decrease": 0.0, "stable": 0.0, "increase": 0.0}
    for d_term, d_mu in d.items():
        if d_mu == 0:
            continue
        for s_term, s_mu in s.items():
            if s_mu == 0:
                continue
            for i_term, i_mu in i.items():
                if i_mu == 0:
                    continue
                strength = min(d_mu, s_mu, i_mu)
                cons = rule_output(d_term, s_term, i_term)
                w[cons] = max(w[cons], strength)

    numerator = 0.0
    denominator = 0.0
    for y in range(0, 101):
        mu = max(
            min(mu_decrease(y), w["decrease"]),
            min(mu_stable(y), w["stable"]),
            min(mu_increase(y), w["increase"]),
        )
        numerator += y * mu
        denominator += mu

    if denominator == 0:
        return 50.0  
    return numerator / denominator


def calculate():
    try:
        demand = float(entry_demand.get())
        supply = float(entry_supply.get())
        inflation = float(entry_inflation.get())

        demand = clamp01(demand)
        supply = clamp01(supply)
        inflation = clamp01(inflation)

        growth = predict_energy_price_growth(demand, supply, inflation)
        result_label.config(text=f"Predicted growth: {growth:.2f}%")

        if growth > 60:
            comment_label.config(text="Expected price increase", fg="red")
        elif growth < 40:
            comment_label.config(text="Expected price decrease", fg="blue")
        else:
            comment_label.config(text="Prices expected to remain stable", fg="green")
    except ValueError:
        result_label.config(text="Error: enter numeric values!")
        comment_label.config(text="")


root = Tk()
root.title("lab05")
root.geometry("400x280")
root.resizable(False, False)

title_label = tk.Label(root, text="Economic Trend Forecast", font=("Arial", 14, "bold"))
title_label.pack(pady=10)

frame_demand = ttk.Frame(root)
frame_demand.pack(pady=5)
tk.Label(frame_demand, text="Demand (%):").pack(side="left", padx=5)
entry_demand = ttk.Entry(frame_demand, width=10)
entry_demand.pack(side="left")

frame_supply = ttk.Frame(root)
frame_supply.pack(pady=5)
tk.Label(frame_supply, text="Supply (%):").pack(side="left", padx=5)
entry_supply = ttk.Entry(frame_supply, width=10)
entry_supply.pack(side="left")

frame_inflation = ttk.Frame(root)
frame_inflation.pack(pady=5)
tk.Label(frame_inflation, text="Inflation (%):").pack(side="left", padx=5)
entry_inflation = ttk.Entry(frame_inflation, width=10)
entry_inflation.pack(side="left")

calc_button = ttk.Button(root, text="Calculate", command=calculate)
calc_button.pack(pady=15)

result_label = tk.Label(root, text="", font=("Arial", 12))
result_label.pack(pady=5)

comment_label = tk.Label(root, text="", font=("Arial", 11, "italic"))
comment_label.pack()

root.mainloop()

