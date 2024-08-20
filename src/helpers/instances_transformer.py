import re


def read_tasks_from_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()

    tasks = []
    durations = []
    resources = []
    precedence_section = False
    durations_section = False
    current_durations = []
    current_resources = []

    for line in lines:
        line = line.strip()
        if "PRECEDENCE RELATIONS:" in line:
            precedence_section = True
            durations_section = False
            continue
        if "REQUESTS/DURATIONS" in line:
            precedence_section = False
            durations_section = True
            continue
        if precedence_section:
            if re.match(r"^\d", line):
                parts = re.split(r"\s+", line)
                try:
                    successors = list(map(int, parts[3:]))
                    tasks.append(successors)
                except ValueError:
                    continue  # Skip any lines that don't match the expected format
        if durations_section:
            if line.startswith(
                "************************************************************************"
            ):
                break
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
    return tasks, durations[1:], resources[1:]


filename = "instance.txt"
tasks_successors, tasks_durations, task_resources = read_tasks_from_file(filename)
print(f"SUCCESSORS = {tasks_successors}")
print(f"DURATIONS = {tasks_durations}")
print(f"RESOURCE_USAGE = {task_resources}")
