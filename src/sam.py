import copy
import random
import importlib
import os
import sys
import numpy as np

from dotenv import load_dotenv

load_dotenv()

INSTANCE_NAME = sys.argv[1]
INSTANCE_SIZE = sys.argv[2]

CHAINS = int(sys.argv[3])
STEPS = int(sys.argv[4])
NEIGHBOURS_INITIAL_N = int(sys.argv[5])
NEIGHBOURS_INCREASE_COEFFICIENT = int(sys.argv[6])
TEMPERATURE_MAX = int(sys.argv[7])
TEMPERATURE_DECREASE_COEFFICIENT = float(sys.argv[8])

PRINT_SCHEDULE = os.getenv("PRINT_SCHEDULE", "False") == "True"

current_instance = importlib.import_module(
    f"helpers.sam.{INSTANCE_SIZE}.{INSTANCE_NAME}"
)


def last_predecessor_finish_time(task, schedule):
    predecessors = current_instance.PREDECESSORS[task - 1]

    if len(predecessors) == 0:
        return 0

    finish_time = -1

    for predecessor in predecessors:
        i = predecessor - 1
        if finish_time == -1 or schedule[i][3] > finish_time:
            finish_time = schedule[i][3]

    return finish_time


def last_predecessor_index(task_index, activities):
    predecessors = current_instance.PREDECESSORS[activities[task_index] - 1]

    if len(predecessors) == 0:
        return -1

    for i in range(task_index - 1, -1, -1):
        if activities[i] in predecessors:
            return i

    return -1


def first_successor_index(task_index, solution):
    successors = current_instance.SUCCESSORS[solution[task_index] - 1]

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

    tasks = copy.deepcopy(current_instance.PREDECESSORS)

    options = []

    for i, task in enumerate(tasks):
        if len(task) == 0:
            options.append(i + 1)

    while True:
        if len(options) == 0:
            break

        # task_selected, mode_selected = shortest_process_time_heuristic(options)
        task_selected, mode_selected = less_resourceful_heuristic(options)

        activities.append(task_selected)
        modes.append(mode_selected)

        tasks[task_selected - 1] = [-1]
        options.remove(task_selected)

        for i, _ in enumerate(tasks):
            if task_selected in tasks[i]:
                tasks[i].remove(task_selected)
                if len(tasks[i]) == 0:
                    options.append(i + 1)

    while not nonrenewable_resources_constraints_met(activities, modes):
        modes = generate_mode_neighbour(activities, modes)

    return activities, modes


def shortest_process_time_heuristic(options):
    task = -1
    mode = -1
    spt = -1

    for option in options:
        for m, duration in enumerate(current_instance.DURATIONS[option - 1]):
            if spt == -1 or duration < spt:
                task = option
                mode = m
                spt = duration

    return task, mode


def less_resourceful_heuristic(options):
    task = -1
    mode = -1
    r = -1

    for option in options:
        for m, resources in enumerate(current_instance.RESOURCE_USAGE[option - 1]):
            sum_r = sum(resources[current_instance.RESOURCES_RENEW :])

            if r == -1 or r > sum_r:
                task = option
                mode = m
                r = sum_r

    return task, mode


def generate_activity_neighbour(activities, modes):
    task_index = random.randint(0, len(activities) - 1)

    last_predecessor = last_predecessor_index(task_index, activities)
    first_successor = first_successor_index(task_index, activities)

    if first_successor == -1:
        first_successor = len(activities)

    trials = 0
    max_trials = 5

    selection = random.randint(last_predecessor + 1, first_successor - 1)

    while trials < max_trials and selection == task_index:
        trials += 1
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


def generate_mode_neighbour(activities, modes, trials=5):
    rand_index = random.randint(0, len(current_instance.PREDECESSORS) - 1)

    n_modes = len(current_instance.DURATIONS[0])
    r = random.randint(1, n_modes - 1)
    new_mode = (modes[rand_index] + r) % n_modes

    modes_neighbour = list(modes)
    modes_neighbour[rand_index] = new_mode

    if not nonrenewable_resources_constraints_met(activities, modes_neighbour):
        if trials == 0:
            return modes
        return generate_mode_neighbour(activities, modes, trials - 1)

    return modes_neighbour


def nonrenewable_resources_constraints_met(activities, modes):
    resources_used = [0] * current_instance.RESOURCES_NONRENEW

    for i, task in enumerate(activities):
        for j in range(0, current_instance.RESOURCES_NONRENEW):
            resources_used[j] += current_instance.RESOURCE_USAGE[task - 1][modes[i]][
                current_instance.RESOURCES_RENEW + j
            ]
            if (
                resources_used[j]
                > current_instance.RESOURCE_LIMITS[current_instance.RESOURCES_RENEW + j]
            ):
                return False

    return True


def cost(activities, modes, show=False):
    schedule = [(-1, -1, 0, 0)] * len(current_instance.PREDECESSORS)

    start_time = 0

    task = activities[0]
    duration = current_instance.DURATIONS[task - 1][modes[0]]
    finish_time = start_time + duration

    schedule[task - 1] = (task, modes[0], start_time, finish_time)

    total = finish_time

    milestones = [start_time]

    if start_time != finish_time:
        milestones.append(finish_time)

    for i in range(1, len(activities)):

        task = activities[i]
        mode = modes[i]
        duration = current_instance.DURATIONS[task - 1][mode]

        last_predecessor_finish = last_predecessor_finish_time(task, schedule)
        previous_task_start_time = schedule[activities[i - 1] - 1][2]

        # Must be scheduled at least at start time from previous task
        # Must be scheduled after last predecessor finish time
        # Must be scheduled with enough resources

        start = previous_task_start_time

        if last_predecessor_finish > start:
            start = last_predecessor_finish

        milestone_start_index = find_index(milestones, start)
        for j in range(milestone_start_index, len(milestones)):
            milestone = milestones[j]
            start = milestone
            if is_enough_resources(
                schedule, task, mode, milestone, milestone + duration
            ):
                break

        finish = start + duration

        schedule[task - 1] = (task, mode, start, finish)

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
    resources = list(
        current_instance.RESOURCE_LIMITS[: current_instance.RESOURCES_RENEW]
    )

    task_resources = current_instance.RESOURCE_USAGE[task - 1][mode]
    for i in range(0, current_instance.RESOURCES_RENEW):
        resources[i] -= task_resources[i]

    for scheduled_task in schedule:
        t, m, start, finish = scheduled_task
        if does_overlap((start_time, finish_time), (start, finish)):
            scheduled_task_resources = current_instance.RESOURCE_USAGE[t - 1][m]
            for i in range(0, current_instance.RESOURCES_RENEW):
                resources[i] -= scheduled_task_resources[i]
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

    for _ in range(CHAINS):
        current_temperature = TEMPERATURE_MAX
        for step in range(1, STEPS + 1):
            n = NEIGHBOURS_INITIAL_N * (1 + NEIGHBOURS_INCREASE_COEFFICIENT * step)
            for _ in range(n):
                neighbour_activities = list(current_activities)
                neighbour_modes = list(current_modes)

                if random.randint(0, 1) == 1:
                    neighbour_activities, neighbour_modes = generate_activity_neighbour(
                        current_activities, current_modes
                    )
                else:
                    neighbour_modes = generate_mode_neighbour(
                        current_activities, current_modes
                    )

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
                    current_activities = list(neighbour_activities)
                    current_modes = list(neighbour_modes)
                    current_cost = neighbour_cost
            current_temperature = (
                TEMPERATURE_DECREASE_COEFFICIENT**step
            ) * TEMPERATURE_MAX

    return best_activities, best_modes, best_cost
