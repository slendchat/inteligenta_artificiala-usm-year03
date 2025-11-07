import tkinter as tk
from tkinter import ttk
from enum import Enum

class States(Enum):
  low = "low"
  mid = "mid"
  high = "high"

class Mamdani_rule:
  def __init__(self, demand_state, supply_state, inflation_state, result_state):
    self.demand_state = demand_state
    self.supply_state = supply_state
    self.inflation_state = inflation_state
    self.result_state = result_state

  def evaluate(self, demand_fuzzy, supply_fuzzy, inflation_fuzzy):
    delta_demand = demand_fuzzy[self.demand_state]
    delta_supply = supply_fuzzy[self.supply_state]
    delta_inflation = inflation_fuzzy[self.inflation_state]

    strength = min(delta_demand, delta_supply, delta_inflation)

    return self.result_state, strength


#        ^
# 1.0    |        /\
#        |       /  \
#        |______/____\______
#         0   30   60   100
#           low  mid   high
# При 20 → “low” = 0.7, “mid” = 0.3
# При 60 → “mid” = 1.0, остальные = 0
# При 80 → “high” = 0.8
class FuzzyTerm:
  def __init__(self, name: States, begin: float, spike: float, end: float):
    self.name = name
    self.begin = begin
    self.spike = spike 
    self.end = end 

  def membership(self, value: float) -> float:
    if value <= self.begin or value >= self.end:
      return 0.0
    elif value == self.spike:
      return 1.0
    elif value < self.spike:
      return (value - self.begin) / (self.spike - self.begin)
    else: 
      return (self.end - value) / (self.end - self.spike)


class Demand:
  LOW_THRESHOLD = 30
  HIGH_THRESHOLD = 70

  def __init__(self,value):
    self.value = value
    self.state = self.get_state(value)
    self.terms = {
      States.low:  FuzzyTerm(States.low, 0, 0, 50),
      States.mid:  FuzzyTerm(States.mid, 30, 60, 90),
      States.high: FuzzyTerm(States.high, 70, 100, 100),
    }

  def get_state(self,value):
    if value < self.LOW_THRESHOLD:
      return States.low
    elif value < self.HIGH_THRESHOLD:
      return States.mid
    else:
      return States.high
    
  def fuzzify(self):
    return {name: term.membership(self.value) for name, term in self.terms.items()}

class Supply:
  LOW_THRESHOLD = 30
  HIGH_THRESHOLD = 70

  def __init__(self,value):
    self.value = value
    self.state = self.get_state(value)
    self.terms = {
      States.low:  FuzzyTerm(States.low, 0, 0, 50),
      States.mid:  FuzzyTerm(States.mid, 30, 60, 90),
      States.high: FuzzyTerm(States.high, 70, 100, 100),
    }

  def get_state(self,value):
    if value < self.LOW_THRESHOLD:
      return States.low
    elif value < self.HIGH_THRESHOLD:
      return States.mid
    else:
      return States.high
    
  def fuzzify(self):
    return {name: term.membership(self.value) for name, term in self.terms.items()}

class Inflation:
  LOW_THRESHOLD = 50

  def __init__(self,value):
    self.value = value
    self.state = self.get_state(value)
    self.terms = {
      States.low:  FuzzyTerm(States.low, 0, 0, 50),
      States.high: FuzzyTerm(States.high, 50, 100, 100),
    }

  def get_state(self,value):
    if value < self.LOW_THRESHOLD:
      return States.low
    else:
      return States.high

  def fuzzify(self):
    return {name: term.membership(self.value) for name, term in self.terms.items()}





def calculate(demand_value, supply_value, inflation_value, result_label=None, comment_label=None):
  demand = Demand(demand_value)
  supply = Supply(supply_value)
  inflation = Inflation(inflation_value)

  demand_fuzzified = demand.fuzzify()
  supply_fuzzified = supply.fuzzify()
  inflation_fuzzified = inflation.fuzzify()

  rule_raise = Mamdani_rule(States.high, States.low,  States.high, States.high)
  rule_drop = Mamdani_rule(States.low,  States.high, States.low,  States.low)
  rule_stability = Mamdani_rule(States.mid,  States.mid,  States.high,  States.high)

  rules = [rule_raise, rule_drop, rule_stability]
  results = {States.low: 0.0, States.mid: 0.0, States.high: 0.0}

  for rule in rules:
    results_state, strength = rule.evaluate(demand_fuzzified, supply_fuzzified, inflation_fuzzified)
    results[results_state] = max(results[results_state], strength)
  final_state = max(results, key=results.get)
  confidence = results[final_state]
  
  text = f"Predicted trend: {final_state.value.upper()} ({confidence:.2f})"
  comment = ""
  if final_state == States.high:
    comment = "Expected price increase"
  elif final_state == States.mid:
    comment = "Prices remain stable"
  else:
    comment = "Expected price decrease"
  if result_label:
    result_label.config(text=text)
  if comment_label:
    comment_label.config(text=comment)

def main():
  root = tk.Tk()
  root.title("lab05")
  root.geometry("400x280")
  root.resizable(False, False)

  title_label = tk.Label(root, text="Economic Trend", font=("Arial", 14, "bold"))
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

  calc_button = ttk.Button(
    root, 
    text="Calculate", 
    command=lambda: calculate(
      float(entry_demand.get() or 0),
      float(entry_supply.get() or 0),
      float(entry_inflation.get() or 0),
      result_label,
      comment_label
    )
  )

  calc_button.pack(pady=15)

  result_label = tk.Label(root, text="", font=("Arial", 12))
  result_label.pack(pady=5)

  comment_label = tk.Label(root, text="", font=("Arial", 11, "italic"))
  comment_label.pack()

  root.mainloop()

if __name__ == "__main__":
  main()