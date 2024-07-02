import copy
import random
import time
import numpy as np


def calculate_critical_path():
    return 0


def generate_activity_initial_solution():
    return []


def shortest_process_time(solution):
    return len(solution)


def generate_activity_neighbour(solution):
    return solution


def acceptance_threshold(temperature, delta):
    return np.exp(-delta / temperature) > random.uniform(0.0, 1.0)


def sa_procedure():
    cp = calculate_critical_path()
    x0 = generate_activity_initial_solution()
    cost_x0 = shortest_process_time(x0)
    x_best = list(x0)
    cost_best = cost_x0
    x_current = list(x0)
    cost_current = cost_x0

    n0 = 1_000  # or 10_000
    h = 1
    t0_max = 100
    alpha = 0.25
    s = 5
    c = 2

    for _ in range(c):
        t = t0_max
        n = n0
        for step in range(1, s + 1):
            n = n * (1 + h * step)
            for _ in range(n):
                x_neighbour = generate_activity_neighbour(x_current)
                cost_x_neighbour = shortest_process_time(x_neighbour)
                delta = cost_x_neighbour - cost_current
                if delta < 0:
                    x_current = x_neighbour
                    cost_current = cost_x_neighbour

                    if cost_x_neighbour < cost_best:
                        x_best = x_neighbour
                        cost_best = cost_x_neighbour

                        if cost_best == cp:
                            return x_best
                elif acceptance_threshold(t, delta):
                    x_current = x_neighbour
                    cost_current = cost_x_neighbour
            t = (alpha**step) * t0_max

    return x_best


start_time = time.time()
sa_solution = sa_procedure()
end_time = time.time()

print(f"Best Solution so far: {sa_solution}")

print(f"Execution time: {end_time - start_time} seconds")
