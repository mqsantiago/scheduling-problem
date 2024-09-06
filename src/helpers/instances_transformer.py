import re
import sys
import os

# Recursively get all files in the instances directory
filepaths = []
for root, dirs, files in os.walk("instances/"):
    for file in files:
        if file.endswith(".mm"):  # Filter to only get .mm files
            filepaths.append(os.path.join(root, file))

if len(filepaths) == 0:
    print("No files found in dir")
    sys.exit(0)

# Extract instance names and maintain the directory structure
instance_names = [
    os.path.relpath(fp, "instances/").rsplit(".", 1)[0] for fp in filepaths
]


def read_tasks_from_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    tasks = []
    durations = []
    resources = []
    resources_avail = []
    precedence_section = False
    durations_section = False
    resource_section = False
    current_durations = []
    current_resources = []

    for line in lines:
        line = line.strip()
        if "PRECEDENCE RELATIONS:" in line:
            precedence_section = True
            durations_section = False
            resource_section = False
            continue

        if "REQUESTS/DURATIONS" in line:
            precedence_section = False
            durations_section = True
            resource_section = False
            continue

        if "RESOURCE AVAILABILITIES" in line or "RESOURCEAVAILABILITIES" in line:
            precedence_section = False
            durations_section = False
            resource_section = True
            continue

        if resource_section:
            if re.match(r"^\d", line):
                parts = re.split(r"\s+", line)
                try:
                    resources_avail = list(map(int, parts))
                except ValueError:
                    continue  # Skip any lines that don't match the expected format

        if precedence_section:
            if re.match(r"^\d", line):
                parts = re.split(r"\s+", line)
                try:
                    successors = list(map(int, parts[3:]))
                    tasks.append(successors)
                except ValueError:
                    continue  # Skip any lines that don't match the expected format

        if durations_section:
            if re.match(r"^\d", line):
                parts = re.split(r"\s+", line)
                try:
                    i = 1
                    if len(parts) == 7:
                        i = 2
                        durations.append(current_durations)
                        resources.append(current_resources)
                        current_durations = []
                        current_resources = []
                    current_durations.append(int(parts[i]))
                    current_resources.append(list(map(int, parts[i + 1 :])))
                except ValueError:
                    continue  # Skip any lines that don't match the expected format
    durations.append(durations[1])
    resources.append(resources[1])
    return tasks, durations[1:], resources[1:], resources_avail


def predecessors_from_successors(all_successors):
    predecessors = [[] for _ in all_successors]

    for task, successors in enumerate(all_successors):
        for successor in successors:
            predecessors[successor - 1].append(task + 1)

    for i, i_p in enumerate(predecessors):
        for j, j_p in enumerate(predecessors):
            if i + 1 in j_p:
                predecessors[j].extend(i_p)

    for i, _ in enumerate(predecessors):
        predecessors[i] = list(set(predecessors[i]))
        predecessors[i].sort()

    return predecessors


def ensure_directory_exists(path):
    os.makedirs(path, exist_ok=True)


def generate_savile_row_file(path, **params):
    ensure_directory_exists(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as output_file:
        output_file.write("language ESSENCE' 1.0\n\n")
        for key, value in params.items():
            output_file.write(f"letting {key} = {value}\n")


def generate_sam_file(path, **params):
    ensure_directory_exists(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as output_file:
        for key, value in params.items():
            output_file.write(f"{key.upper()} = {value}\n")


for instance_name, filepath in zip(instance_names, filepaths):

    tasks_successors, tasks_durations, task_resources, avail = read_tasks_from_file(
        filepath
    )

    HORIZON = sum(max(i) for i in tasks_durations)

    JOBS = len(tasks_durations)

    print(f"Generating Savile for {instance_name}")
    generate_savile_row_file(
        f"sr/{instance_name}.param",
        jobs=JOBS,
        horizon=HORIZON,
        resourcesRenew=2,
        resourcesNonrenew=2,
        resourceLimits=avail,
        successors=tasks_successors,
        durations=tasks_durations,
        resourceUsage=task_resources,
    )

    print(f"Generating SAM for {instance_name}")
    tasks_durations[0] = tasks_durations[0] * len(tasks_durations[1])
    tasks_durations[-1] = tasks_durations[0]

    task_resources[0] = task_resources[0] * len(task_resources[1])
    task_resources[-1] = task_resources[0]

    task_predecessors = predecessors_from_successors(tasks_successors)

    generate_sam_file(
        f"sam/{instance_name}.py",
        jobs=JOBS,
        resources_renew=2,
        resources_nonrenew=2,
        resource_limits=avail,
        successors=tasks_successors,
        durations=tasks_durations,
        resource_usage=task_resources,
        predecessors=task_predecessors,
    )

print("DONE!")
