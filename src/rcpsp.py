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

    if len(predecessors) == 0:
        return -1

    for i in range(task_index - 1, -1, -1):
        if solution[i] in predecessors:
            return i

    return -1


def first_successor_index(task_index, solution):
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
    task_index = random.randint(0, len(solution) - 1)

    last_predecessor = last_predecessor_index(task_index, solution)
    first_successor = first_successor_index(task_index, solution)

    if first_successor == -1:
        first_successor = len(solution)

    selection = random.randint(last_predecessor + 1, first_successor - 1)

    if selection == task_index:
        return solution

    return cycle_swift(solution, task_index, selection)


def cycle_swift(s, pivot, edge):
    n = list(s)

    if pivot < edge:
        n[pivot:edge] = s[pivot + 1 : edge + 1]
    else:
        n[edge + 1 : pivot + 1] = s[edge:pivot]

    n[edge] = s[pivot]
    return n


def cost(activities, show=False):
    schedule = [(-1, 0, 0)] * len(params.PREDECESSORS)

    start_time = 0

    task = activities[0]
    duration = params.DURATIONS[task - 1][0]
    finish_time = start_time + duration

    schedule[task - 1] = (task, start_time, finish_time)

    total = finish_time

    milestones = [start_time]

    if start_time != finish_time:
        milestones.append(finish_time)

    for i in range(1, len(activities)):

        task = activities[i]

        last_predecessor = last_predecessor_index(i, activities)

        last_predecessor_finish_time = schedule[activities[last_predecessor] - 1][2]
        previous_task_start_time = schedule[activities[i - 1] - 1][1]

        # Must be scheduled at least at start time from previous task
        # Must be scheduled after last predecessor finish time
        # Must be scheduled with enough resources

        start = previous_task_start_time

        if last_predecessor_finish_time > start:
            start = last_predecessor_finish_time

        milestone_start_index = find_index(milestones, start)
        for j in range(milestone_start_index, len(milestones)):
            milestone = milestones[j]
            start = milestone
            if is_enough_resources(schedule, task, milestone):
                break

        # start = milestones[milestone_start_index]

        duration = params.DURATIONS[task - 1][0]
        finish = start + duration

        schedule[task - 1] = (task, start, finish)  # type: ignore

        si = find_index(milestones, start)

        if milestones[si] != start:
            milestones.insert(si + 1, start)

        fi = find_index(milestones, finish)
        if milestones[fi] != finish:
            milestones.insert(fi + 1, finish)

        if finish > total:
            total = finish

    if show:
        print_schedule(schedule, activities)

    return total


def find_index(arr, value, first=True):
    if first:
        arr = list(enumerate(arr))

    size = len(arr)

    if size == 0:
        return -1

    if size == 1:
        return arr[0][0]

    middle = int(size / 2)

    if arr[middle][1] == value:
        return arr[middle][0]

    if arr[middle][1] > value:
        return find_index(arr[:middle], value, False)
    return find_index(arr[middle:], value, False)


def print_schedule(schedule, activities):
    ordered_schedule = []

    for i in activities:
        ordered_schedule.append(schedule[i - 1])

    print(ordered_schedule)
    for item in ordered_schedule:
        print(f"{item[0]}", end=" ")
        max_size = item[1] if item[0] > 9 else item[1] + 1
        for _ in range(max_size):
            print(" ", end="")
        for _ in range(item[2] - item[1]):
            print("-", end="")
        print("")
    print("")


def is_enough_resources(schedule, task, start_time):
    resources = list(params.RESOURCE_LIMITS)

    task_resources = params.RESOURCE_USAGE[task - 1][0]
    for i, resource in enumerate(task_resources):
        resources[i] -= resource

    for scheduled_task in schedule:
        t, start, end = scheduled_task
        if start <= start_time < end:
            scheduled_task_resources = params.RESOURCE_USAGE[t - 1][0]
            for i, resource in enumerate(scheduled_task_resources):
                resources[i] -= resource
                if resources[i] < 0:
                    return True

    return True


def acceptance_threshold(temperature, delta):
    return np.exp(-delta / temperature) > random.uniform(0.0, 1.0)


def sa_procedure():
    # cp = calculate_critical_path()
    # print(cp)
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
    s = 1  # 5
    c = 1  # 2

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
                    x_current = list(x_neighbour)
                    cost_current = cost_x_neighbour

                    if cost_x_neighbour < cost_best:
                        x_best = list(x_neighbour)
                        cost_best = cost_x_neighbour

                        # if cost_best <= cp:
                        # return x_best
                elif acceptance_threshold(t, delta):
                    x_current = x_neighbour
                    cost_current = cost_x_neighbour
            t = (alpha**step) * t0_max

    return x_best


help_start_time = time.time()
sa_solution = sa_procedure()
help_end_time = time.time()

print(f"Best Solution so far: {sa_solution}")

print(cost(sa_solution, True))

print(f"Execution time: {help_end_time - help_start_time} seconds")
