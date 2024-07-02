import copy
import random
import time
import numpy as np

DURATION_INDEX = 0
RESOURCE_1_INDEX = 1
RESOURCE_2_INDEX = 2
RESOURCE_3_INDEX = 3

TASKS_DETAILS = [
    (5, 5, 3, 2),  # 1
    (5, 4, 5, 3),  # 2
    (3, 2, 5, 2),  # 3
    (4, 1, 4, 4),  # 4
    (2, 4, 2, 4),  # 5
    (1, 5, 5, 4),  # 6
    (6, 5, 3, 2),  # 7
    (6, 2, 3, 2),  # 8
    (1, 1, 4, 4),  # 9
    (3, 2, 3, 4),  # 10
    (3, 3, 3, 2),  # 11
    (3, 4, 1, 4),  # 12
    (3, 5, 5, 4),  # 13
    (6, 2, 2, 2),  # 14
    (4, 5, 1, 4),  # 15
    (3, 3, 5, 3),  # 16
    (3, 2, 3, 3),  # 17
    (4, 5, 4, 4),  # 18
    (1, 4, 2, 6),  # 19
    (4, 0, 1, 4),  # 20
    (4, 6, 1, 2),  # 21
    (1, 2, 2, 1),  # 22
    (6, 2, 3, 1),  # 23
    (3, 2, 2, 2),  # 24
    (3, 1, 0, 3),  # 25
]

TASKS_PRECEDENCE = [
    [],
    [],
    [],
    [0, 1],
    [0, 1],
    [2],
    [2],
    [3, 4, 6],
    [3],
    [4, 5, 6],
    [5],
    [7, 9],
    [7],
    [8],
    [10],
    [11],
    [13],
    [12, 14],
    [14],
    [15],
    [15, 16],
    [17],
    [17, 18],
    [19],
    [19, 20, 21, 22],
]


def greater_than(s, a, b):
    return s[a] > s[b]


CONSTRAINTS = [
    (index, task) for index, tasks in enumerate(TASKS_PRECEDENCE) for task in tasks
]

INITIAL_TEMPERATURE = 1000
LENGTH = 25
RESOURCE_LIMIT = 6


def is_constraints_satisfied(solution):
    results = [greater_than(solution, c[0], c[1]) for c in CONSTRAINTS]
    return all(results)


def generate_initial_solution():
    priority = 1

    solution = [-1] * LENGTH

    tasks = copy.deepcopy(TASKS_PRECEDENCE)

    while True:
        options = [
            index if len(task) == 0 else None for index, task in enumerate(tasks)
        ]

        available_options = list(filter(lambda option: option is not None, options))

        if len(available_options) == 0:
            break

        selection = random.choice(available_options)

        if selection is None:
            continue

        solution[selection] = priority

        priority += 1

        tasks[selection] = [-1]

        for i, _ in enumerate(tasks):
            if selection in tasks[i]:
                tasks[i].remove(selection)

    return solution


def neighbour(solution):
    options = list(range(LENGTH))

    while len(options) != 0:
        selection = random.choice(options)
        options.remove(selection)

        domain = list(range(LENGTH))
        while len(domain) != 0:
            new_solution = copy.deepcopy(solution)

            new_priority = random.choice(domain)

            aux = new_solution[selection]
            new_solution[selection] = new_solution[new_priority]
            new_solution[new_priority] = aux

            if is_constraints_satisfied(new_solution):
                return new_solution

            domain.remove(new_priority)

    return solution


def cost(solution, show=False):
    project_end = 0
    priorities = list(enumerate(solution))

    priorities.sort(key=lambda item: item[1])

    schedule = []
    milestones = {}

    for [task, _] in priorities:
        task_start, task_end = schedule_task(task, schedule, milestones)

        schedule.append((task, task_start, task_end))

        create_milestone(milestones, task, task_start, task_end, schedule)

        if task_end > project_end:
            project_end = task_end

    if show:
        print_schedule(schedule)

    return project_end


def schedule_task(task, schedule, milestones):
    task_start = last_predecessor_end_time(schedule, task)

    duration = TASKS_DETAILS[task][DURATION_INDEX]

    m_keys = list(milestones.keys())
    m_keys.sort()

    i = 0
    if len(m_keys) != 0:
        i = find_index(m_keys, task_start)

    # print(f"task {task + 1}")
    # print(f"{milestones}")
    for index in range(i, len(m_keys)):
        milestone_time = m_keys[index]

        provisional_task_end = milestone_time + duration

        enough_resources = is_enough_resources(
            task, milestone_time, provisional_task_end, milestones, m_keys
        )

        if enough_resources:
            task_start = milestone_time
            break
    # print(task_start)

    return task_start, task_start + duration


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


# BUG: Nao somente criando os milestones de inicio e fim logo parece que ao criar um novo milestone
# a task somente usa os recursos por um unico instante e nao o tempo de duracao real dela.
def is_enough_resources(task, milestone_time, provisional_task_end, milestones, m_keys):
    r1 = TASKS_DETAILS[task][RESOURCE_1_INDEX]
    r2 = TASKS_DETAILS[task][RESOURCE_2_INDEX]
    r3 = TASKS_DETAILS[task][RESOURCE_3_INDEX]

    i_start = find_index(m_keys, milestone_time)
    i_end = find_index(m_keys, provisional_task_end)

    if i_start == i_end and i_end < len(m_keys) - 1:
        i_end += 1

    # print(
    #     f"task {task + 1}, i_start {i_start}, i_end {i_end}, ({m_keys[i_start]}, {m_keys[i_end]})"
    # )
    for i in range(i_start, i_end):
        # print(f"{m_keys[i]} - {milestones[m_keys[i]]}")
        resources = milestones[m_keys[i]]
        is_enough_resource_1 = resources[0] + r1 <= RESOURCE_LIMIT
        is_enough_resource_2 = resources[1] + r2 <= RESOURCE_LIMIT
        is_enough_resource_3 = resources[2] + r3 <= RESOURCE_LIMIT

        if (
            not is_enough_resource_1
            or not is_enough_resource_2
            or not is_enough_resource_3
        ):
            return False

    return True


def last_predecessor_end_time(schedule, task=0, task_start=0):
    if len(TASKS_PRECEDENCE[task]) != 0:
        precedence_end_times = [
            time[2] if time[0] in TASKS_PRECEDENCE[task] else -1 for time in schedule
        ]
        precedence_end_times.sort()
        task_start = precedence_end_times.pop()
    return task_start


def create_milestone(milestones, task, task_start, task_end, schedule):
    if milestones.get(task_start) is None:
        milestones[task_start] = (0, 0, 0)

    if milestones.get(task_end) is None:
        r1_end = 0
        r2_end = 0
        r3_end = 0

        for scheduled_task, start, end in schedule:
            if start < task_end < end:
                r1_end = r1_end + TASKS_DETAILS[scheduled_task][RESOURCE_1_INDEX]
                r2_end = r2_end + TASKS_DETAILS[scheduled_task][RESOURCE_2_INDEX]
                r3_end = r3_end + TASKS_DETAILS[scheduled_task][RESOURCE_3_INDEX]

        milestones[task_end] = (r1_end, r2_end, r3_end)

    r1 = TASKS_DETAILS[task][RESOURCE_1_INDEX]
    r2 = TASKS_DETAILS[task][RESOURCE_2_INDEX]
    r3 = TASKS_DETAILS[task][RESOURCE_3_INDEX]

    for milestone_time, (m_r1, m_r2, m_r3) in milestones.items():
        if milestone_time < task_start or milestone_time >= task_end:
            continue

        milestones[milestone_time] = (m_r1 + r1, m_r2 + r2, m_r3 + r3)


def print_schedule(schedule):
    print(schedule)
    for item in schedule:
        print(f"{item[0] + 1}", end=" ")
        max_size = item[1] if item[0] > 9 else item[1] + 1
        for _ in range(max_size):
            print(" ", end="")
        for _ in range(item[2] - item[1]):
            print("-", end="")
        print("")
    print("")


def acceptance_threshold(temperature, cost_solution1, cost_solution2):
    delta = cost_solution1 - cost_solution2

    return np.exp(-delta / temperature)


def update_temperature(temperature):
    return temperature - 0.1


def termination_conditions_not_met(temperature):
    return temperature > 0


def simulated_annealing():
    current_solution = generate_initial_solution()

    temperature = INITIAL_TEMPERATURE
    cost_current_solution = cost(current_solution)
    new_current_solution = False

    best_solution = (current_solution, cost_current_solution)

    i = 0
    while termination_conditions_not_met(temperature):
        # print(temperature)
        new_solution = neighbour(current_solution)

        cost_new_solution = cost(new_solution)
        if new_current_solution:
            cost_current_solution = cost(current_solution)

        if cost_new_solution < cost_current_solution or acceptance_threshold(
            temperature, cost_current_solution, cost_new_solution
        ):
            current_solution = new_solution
            new_current_solution = True
        else:
            new_current_solution = False

        if cost_current_solution < best_solution[1]:
            best_solution = (current_solution, cost_current_solution)
            i = 0
        else:
            i += 1

        temperature = update_temperature(temperature)

    return best_solution


start_time = time.time()
sa_solution = simulated_annealing()
end_time = time.time()
# sa_solution = (
#     [
#         4,
#         5,
#         1,
#         6,
#         7,
#         3,
#         2,
#         9,
#         14,
#         10,
#         8,
#         17,
#         12,
#         18,
#         11,
#         20,
#         19,
#         13,
#         16,
#         22,
#         21,
#         15,
#         24,
#         23,
#         25,
#     ],
#     64,
# )

print(sa_solution)
c = cost(sa_solution[0], True)
print(c)

print(f"Execution time: {end_time - start_time} seconds")

# available_resources = [RESOURCE_LIMIT, RESOURCE_LIMIT, RESOURCE_LIMIT]
# for scheduled_item in schedule:
#   scheduled_task, start, end = scheduled_item
#   m_end = milestone + task_duration
#   if start <= m_end and start >= milestone or end > milestone and end < m_end or start <= m_end and end > milestone or start <= milestone and end > m_end:
#     available_resources[0] = available_resources[0] - TASKS_DETAILS[scheduled_task][RESOURCE_1_INDEX]
#     available_resources[1] = available_resources[1] - TASKS_DETAILS[scheduled_task][RESOURCE_2_INDEX]
#     available_resources[2] = available_resources[2] - TASKS_DETAILS[scheduled_task][RESOURCE_3_INDEX]
