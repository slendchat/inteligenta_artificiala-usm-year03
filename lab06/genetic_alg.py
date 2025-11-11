from typing import List
import random
import math

# function x * sin(10 * x) x=[0;1]
def math_func(x:float) -> float:
  return (x * math.sin(10*x))

class Genetic_entity():
  def __init__(self, x=None):
    self.x = x if x is not None else random.uniform(0.0, 1.0)
    self.fitness = 0.0

  def mutate(self, pm: float):
    if random.uniform(0.0, 1.0) < pm:
      old_x = self.x
      self.x += random.uniform(-0.1, 0.1)
      self.x = min(max(self.x, 0.0), 1.0)
      print(f"Мутация: x {old_x:.3f} → {self.x:.3f}")

def evaluate(population: List[Genetic_entity]):
  for entity in population:
    entity.fitness = math_func(entity.x)

def selection(population: List[Genetic_entity]):
  population.sort(key=lambda entity: entity.fitness, reverse=True)
  survivors = population[:len(population)//2]
  return survivors

def crossover(parents: List[Genetic_entity], pc: float, target_size: int) -> List[Genetic_entity]:
  children = []
  while len(children) < target_size:
    p1, p2 = random.sample(parents, 2)
    if random.random() < pc:
      alpha = random.random()
      child1_x = alpha * p1.x + (1 - alpha) * p2.x
      child2_x = alpha * p2.x + (1 - alpha) * p1.x
      print(f"Кроссовер: {p1.x:.3f} и {p2.x:.3f} → {child1_x:.3f}, {child2_x:.3f}")
    else:
      child1_x, child2_x = p1.x, p2.x
    children.append(Genetic_entity(child1_x))
    if len(children) < target_size:
      children.append(Genetic_entity(child2_x))
  return children[:target_size]


def main():
  N = 50      # размер популяции
  G = 5       # поколений
  pc = 0.8     # вероятность кроссовера
  pm = 0.1     # вероятность мутации

  population = [Genetic_entity() for _ in range(N)]

  for generation in range(G):
    print(f"\nПоколение {generation + 1}")

    # шаг 1: оценка fitness
    evaluate(population)
    best = max(population, key=lambda e: e.fitness)
    avg_fitness = sum(e.fitness for e in population) / len(population)
    print(f"Лучшее значение: x={best.x:.3f}, f(x)={best.fitness:.3f}")
    print(f"Среднее значение fitness: {avg_fitness:.3f}")

    # шаг 2: отбор лучших
    parents = selection(population)

    # шаг 3: создаём новое поколение потомков
    children = crossover(parents, pc, target_size=N)

    # шаг 4: мутации
    for child in children:
      child.mutate(pm)

    # новое поколение становится популяцией
    population = children

  # финальный результат
  evaluate(population)
  best = max(population, key=lambda e: e.fitness)
  print(f"\n🏁 Лучшее найденное решение: x*={best.x:.4f}, f(x*)={best.fitness:.4f}")

if __name__ == "__main__":
  main()