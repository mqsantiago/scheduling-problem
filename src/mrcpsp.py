import copy
import random
import time
import numpy as np

import params


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
    activities = []
    modes = []

    tasks = copy.deepcopy(params.PREDECESSORS)

    options = []

    for i, task in enumerate(tasks):
        if len(task) == 0:
            options.append(i + 1)

    while True:
        if len(options) == 0:
            break

        task_selected, mode_selected = shortest_process_time(options)

        activities.append(task_selected)
        modes.append(mode_selected)

        tasks[task_selected - 1] = [-1]
        options.remove(task_selected)

        for i, _ in enumerate(tasks):
            if task_selected in tasks[i]:
                tasks[i].remove(task_selected)
                if len(tasks[i]) == 0:
                    options.append(i + 1)

    return activities, modes


def shortest_process_time(options):
    task = -1
    mode = -1
    spt = -1

    for option in options:
        for m, duration in enumerate(params.DURATIONS[option - 1]):
            if spt == -1 or duration < spt:
                task = option
                mode = m
                spt = duration

    return task, mode


def generate_activity_neighbour(activities, modes):
    task_index = random.randint(0, len(activities) - 1)

    last_predecessor = last_predecessor_index(task_index, activities)
    first_successor = first_successor_index(task_index, activities)

    if first_successor == -1:
        first_successor = len(activities)

    selection = random.randint(last_predecessor + 1, first_successor - 1)

    if selection == task_index:
        return activities, modes
    a_n = cycle_swift(activities, task_index, selection)
    m_n = cycle_swift(modes, task_index, selection)

    return a_n, m_n


def cycle_swift(s, pivot, edge):
    n = list(s)

    if pivot < edge:
        n[pivot:edge] = s[pivot + 1 : edge + 1]
    else:
        n[edge + 1 : pivot + 1] = s[edge:pivot]

    n[edge] = s[pivot]
    return n


def generate_mode_neighbour(modes):
    rand_index = random.randint(0, len(params.PREDECESSORS) - 1)

    n_modes = len(params.DURATIONS[0])
    r = random.randint(1, n_modes - 1)
    new_mode = (modes[rand_index] + r) % n_modes

    modes_neighbour = list(modes)
    modes_neighbour[rand_index] = new_mode

    return modes_neighbour


def cost(activities, modes, show=False):
    schedule = [(-1, -1, 0, 0)] * len(params.PREDECESSORS)

    start_time = 0

    task = activities[0]
    duration = params.DURATIONS[task - 1][modes[0]]
    finish_time = start_time + duration

    schedule[task - 1] = (task, modes[0], start_time, finish_time)

    total = finish_time

    milestones = [start_time]

    if start_time != finish_time:
        milestones.append(finish_time)

    for i in range(1, len(activities)):

        task = activities[i]
        duration = params.DURATIONS[task - 1][modes[i]]

        last_predecessor = last_predecessor_index(i, activities)

        last_predecessor_finish_time = schedule[activities[last_predecessor] - 1][3]
        previous_task_start_time = schedule[activities[i - 1] - 1][2]

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
            if is_enough_resources(schedule, task, modes[i], milestone, duration):
                break

        finish = start + duration

        schedule[task - 1] = (task, modes[i], start, finish)

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


def is_enough_resources(schedule, task, mode, start_time, finish_time):
    resources = list(params.RESOURCE_LIMITS)

    task_resources = params.RESOURCE_USAGE[task - 1][mode]
    for i, resource in enumerate(task_resources):
        resources[i] -= resource

    for scheduled_task in schedule:
        t, m, start, finish = scheduled_task
        if does_overlap((start_time, finish_time), (start, finish)):
            scheduled_task_resources = params.RESOURCE_USAGE[t - 1][m]
            for i, resource in enumerate(scheduled_task_resources):
                resources[i] -= resource
                if resources[i] < 0:
                    return False

    return True


def does_overlap(range1, range2):
    return len(range(max(range1[0], range2[0]), min(range1[1], range2[1]))) != 0


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
        t, _, s, f = item
        print(f"{t}", end=" ")
        max_size = s if t > 9 else s + 1
        for _ in range(max_size):
            print(" ", end="")
        for _ in range(f - s):
            print("-", end="")
        print("")
    print("")


def acceptance_threshold(temperature, delta):
    return np.exp(-delta / temperature) > random.uniform(0.0, 1.0)


def sa_procedure():
    initial_activities, initial_modes = generate_activity_initial_solution()

    initial_cost = cost(initial_activities, initial_modes)

    best_activities = list(initial_activities)
    best_modes = list(initial_modes)
    best_cost = initial_cost

    current_activities = list(initial_activities)
    current_modes = list(initial_modes)
    current_cost = initial_cost

    n_neighbours = 1_000  # or 10_000
    h = 1
    temperature_max = 100
    alpha = 0.25
    steps = 1  # 5
    chains = 1  # 2

    for _ in range(chains):
        current_temperature = temperature_max
        n = n_neighbours
        for step in range(1, steps + 1):
            n = n * (1 + h * step)
            for _ in range(n):
                neighbour_activities = list(current_activities)
                neighbour_modes = list(current_modes)

                if random.randint(0, 1) == 1:
                    neighbour_activities, neighbour_modes = generate_activity_neighbour(
                        current_activities, current_modes
                    )
                else:
                    neighbour_modes = generate_mode_neighbour(current_modes)

                neighbour_cost = cost(neighbour_activities, neighbour_modes)
                delta = neighbour_cost - current_cost
                if delta < 0:
                    current_activities = list(neighbour_activities)
                    current_modes = list(neighbour_modes)
                    current_cost = neighbour_cost

                    if neighbour_cost < best_cost:
                        best_activities = list(neighbour_activities)
                        best_modes = list(neighbour_modes)
                        best_cost = neighbour_cost

                elif acceptance_threshold(current_temperature, delta):
                    current_activities = neighbour_activities
                    current_cost = neighbour_cost
            current_temperature = (alpha**step) * temperature_max

    return best_activities, best_modes


help_start_time = time.time()
sa_solution, sa_modes = sa_procedure()
help_end_time = time.time()

print(f"Best Solution so far: \n{sa_solution} \n{sa_modes}")

print(cost(sa_solution, sa_modes, True))

print(f"Execution time: {help_end_time - help_start_time} seconds")
