import copy
import random
import time
import numpy as np

import params


def calculate_critical_path():
    activities = generate_activity_initial_solution()

    schedule = [-1] * len(params.SUCCESSORS)

    critical_path = 0

    for task in activities:
        index = last_scheduled_predecessor_index(task, schedule)

        start_time = 0
        if index != -1:
            start_time = schedule[index]

        duration = params.DURATIONS[task - 1][0]
        finish_time = start_time + duration

        schedule[task - 1] = finish_time

        if finish_time > critical_path:
            critical_path = finish_time

    return critical_path


def last_scheduled_predecessor_index(task, schedule):
    predecessors = params.PREDECESSORS[task - 1]

    index = -1

    if len(predecessors) == 0:
        return index

    for predecessor in predecessors:
        i = predecessor - 1
        if index == -1:
            index = i
            continue

        if schedule[i] > schedule[index]:
            index = i

    return index


def last_predecessor_index(task_index, solution):
    predecessors = params.PREDECESSORS[solution[task_index] - 1]

    index = -1

    if len(predecessors) == 0:
        return index

    for i in range(0, task_index):
        if solution[i] in predecessors:
            index = i

    return index


def first_sucessor_index(task_index, solution):
    successors = params.SUCCESSORS[solution[task_index] - 1]

    index = -1

    if len(successors) == 0:
        return index

    for i in range(task_index + 1, len(solution)):
        if solution[i] in successors:
            return i

    return index


def generate_activity_initial_solution():
    solution = []

    tasks = copy.deepcopy(params.PREDECESSORS)

    options = []

    for i, task in enumerate(tasks):
        if len(task) == 0:
            options.append(i + 1)

    while True:
        if len(options) == 0:
            break

        # selection = random.choice(options)
        selection = shortest_process_time(options)

        if selection is None:
            continue

        solution.append(selection)
        tasks[selection - 1] = [-1]
        options.remove(selection)

        for i, _ in enumerate(tasks):
            if selection in tasks[i]:
                tasks[i].remove(selection)
                if len(tasks[i]) == 0:
                    options.append(i + 1)

    if len(solution) != len(params.PREDECESSORS):
        print(params.ERROR_PRECEDENCE_CYCLE)

    return solution


def shortest_process_time(options):
    task = options[0]
    spt = params.DURATIONS[options[0] - 1][0]

    for i in range(1, len(options)):
        duration = params.DURATIONS[options[i] - 1][0]
        if duration < spt:
            spt = duration
            task = options[i]

    return task


def generate_activity_neighbour(solution):
    neighbour = list(solution)
    task_index = random.randint(0, len(solution) - 1)

    last_predecessor = last_predecessor_index(task_index, solution)
    first_sucessor = first_sucessor_index(task_index, solution)

    if first_sucessor == -1:
        first_sucessor = len(solution)

    selection = random.randint(last_predecessor + 1, first_sucessor - 1)

    start = task_index
    end = selection

    if start > end:
        start = selection
        end = task_index

    neighbour[start + 1 : end + 1] = solution[start:end]
    neighbour[start] = solution[end]

    return neighbour


def cost(solution):
    return len(solution)


def acceptance_threshold(temperature, delta):
    return np.exp(-delta / temperature) > random.uniform(0.0, 1.0)


def sa_procedure():
    # cp = calculate_critical_path()
    x0 = generate_activity_initial_solution()
    cost_x0 = cost(x0)
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
                cost_x_neighbour = cost(x_neighbour)
                delta = cost_x_neighbour - cost_current
                if delta < 0:
                    x_current = x_neighbour
                    cost_current = cost_x_neighbour

                    if cost_x_neighbour < cost_best:
                        x_best = x_neighbour
                        cost_best = cost_x_neighbour

                        # if cost_best == cp:
                        #     return x_best
                elif acceptance_threshold(t, delta):
                    x_current = x_neighbour
                    cost_current = cost_x_neighbour
            t = (alpha**step) * t0_max

    return x_best


help_start_time = time.time()
sa_solution = sa_procedure()
help_end_time = time.time()

print(f"Best Solution so far: {sa_solution}")

print(f"Execution time: {help_end_time - help_start_time} seconds")
