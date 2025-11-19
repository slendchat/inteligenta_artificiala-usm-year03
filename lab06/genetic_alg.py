from typing import List
import random
import math
import argparse
import os

# function x * sin(10 * x) x=[0;1]
def math_func(x: float) -> float:
    return x * math.sin(10 * x)


class Genetic_entity:
    def __init__(self, x=None):
        self.x = x if x is not None else random.uniform(0.0, 1.0)
        self.fitness = 0.0

    def mutate(self, pm: float):
        # mutation operator - with probability pm add small noise and clamp to [0,1]
        if random.uniform(0.0, 1.0) < pm:
            old_x = self.x
            self.x += random.uniform(-0.1, 0.1)
            self.x = min(max(self.x, 0.0), 1.0)
            print(f"mutation in offspring - x {old_x:.4f} -> {self.x:.4f}")


def evaluate(population: List[Genetic_entity]):
    for entity in population:
        entity.fitness = math_func(entity.x)


def selection(population: List[Genetic_entity]):
    # selection operator - truncate selection keeps the top 50 percent to intensify search pressure
    population.sort(key=lambda entity: entity.fitness, reverse=True)
    survivors = population[: len(population) // 2]
    return survivors


def crossover(
    parents: List[Genetic_entity], pc: float, target_size: int
) -> List[Genetic_entity]:
    # crossover operator - arithmetic blend controlled by pc and random alpha, combines parent traits smoothly
    children = []
    pair_index = 0
    while len(children) < target_size:
        p1, p2 = random.sample(parents, 2)
        pair_index += 1
        if random.random() < pc:
            alpha = random.random()
            child1_x = alpha * p1.x + (1 - alpha) * p2.x
            child2_x = alpha * p2.x + (1 - alpha) * p1.x
            print(
                f"crossover in pair {pair_index} - parentA x {p1.x:.4f} and parentB x {p2.x:.4f} - alpha {alpha:.4f}"
            )
        else:
            child1_x, child2_x = p1.x, p2.x
            print(
                f"no crossover in pair {pair_index} - parentA x {p1.x:.4f} and parentB x {p2.x:.4f}"
            )
        children.append(Genetic_entity(child1_x))
        if len(children) < target_size:
            children.append(Genetic_entity(child2_x))
    return children[:target_size]


# helpers for logging a 4-bit representation without changing algorithm logic
L = 4


def x_to_4bit(x: float):
    val = max(0, min((1 << L) - 1, int(round(x * ((1 << L) - 1)))))
    bits = format(val, f"0{L}b")
    return bits, val


def print_population(population: List[Genetic_entity], note: str):
    print(note)
    for idx, e in enumerate(population, start=1):
        bits, dec = x_to_4bit(e.x)
        print(
            f"  individual {idx} - bits {bits} - dec {dec:2d} - x {e.x:.4f} - fitness {e.fitness:.6f}"
        )


def run(N: int, G: int, pc: float, pm: float, plot_path: str, seed: int | None):
    if seed is not None:
        random.seed(seed)

    print("Starting genetic algorithm")
    print(
        f"operators - selection keeps top half, crossover uses arithmetic blend with pc {pc:.3f}, mutation perturbs x with pm {pm:.3f}"
    )

    population = [Genetic_entity() for _ in range(N)]
    max_f_history: List[float] = []

    for generation in range(G):
        print("")
        print(f"Generation {generation + 1}")

        # fitness evaluation
        print("evaluation - computing fitness values for all individuals")
        evaluate(population)
        best = max(population, key=lambda entity: entity.fitness)
        max_f = best.fitness
        min_f = min(entity.fitness for entity in population)
        avg_f = sum(entity.fitness for entity in population) / len(population)
        max_f_history.append(max_f)

        print_population(
            population, note="evaluated population - bits and decimal along with x and fitness"
        )
        print(f"fitness summary - max {max_f:.6f} - min {min_f:.6f} - avg {avg_f:.6f}")

        # selection
        print(
            "selection - keeping the top half by fitness to exploit good solutions while maintaining some diversity"
        )
        parents = selection(population)

        # crossover
        print(
            "crossover - combining parent values through arithmetic blend, this encourages mixing nearby solutions"
        )
        children = crossover(parents, pc, target_size=N)

        # mutation
        print(
            "mutation - applying small random changes to x with pm to explore the space and avoid premature convergence"
        )
        for child in children:
            child.mutate(pm)

        population = children

    # final evaluation and best
    evaluate(population)
    best = max(population, key=lambda entity: entity.fitness)
    print("")
    print(f"final best - x* {best.x:.6f} - f(x*) {best.fitness:.6f}")

    # plot max fitness history
    try:
        import matplotlib.pyplot as plt  # type: ignore

        import os as _os

        _os.makedirs(_os.path.dirname(plot_path) or ".", exist_ok=True)
        plt.figure(figsize=(8, 4))
        plt.plot(range(1, G + 1), max_f_history, marker="o")
        plt.xlabel("generation")
        plt.ylabel("max fitness")
        plt.title("Max fitness over generations")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        print(f"saved plot of max fitness to {plot_path}")
    except Exception as e:
        print(f"plotting skipped - matplotlib not available or failed with error {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simple GA for maximizing f(x) = x * sin(10x) on [0,1]"
    )
    parser.add_argument("--N", type=int, default=50, help="population size N")
    parser.add_argument("--G", type=int, default=5, help="number of generations G")
    parser.add_argument("--pc", type=float, default=0.8, help="crossover probability pc")
    parser.add_argument("--pm", type=float, default=0.1, help="mutation probability pm")
    parser.add_argument(
        "--plot",
        type=str,
        default=os.path.join("lab06", "max_fitness_by_generation.png"),
        help="path to save the max fitness plot",
    )
    parser.add_argument("--seed", type=int, default=None, help="random seed")
    return parser.parse_args()


def main():
    args = parse_args()
    N = max(2, args.N)
    G = max(1, args.G)
    pc = max(0.0, min(1.0, args.pc))
    pm = max(0.0, min(1.0, args.pm))

    print(
        f"parameters - N {N} - G {G} - pc {pc:.3f} - pm {pm:.3f}"
    )
    run(N=N, G=G, pc=pc, pm=pm, plot_path=args.plot, seed=args.seed)


if __name__ == "__main__":
    main()
