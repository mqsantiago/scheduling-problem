import subprocess
import sys

# setting path
sys.path.append("../src")


from src.sam import sa_procedure

FILE_PATH = "src/helpers/sr/30/j3060_1.param"

BASE = "../../../../Downloads/savilerow-1.10.0-linux"

MODIFIERS = "-sat -amo-detect -sat-family kissat -run-solver"


TERMINAL_COMMAND = f"{BASE}/savilerow {MODIFIERS} {BASE}/examples/mrcpsp-pb/mrcpsp-pb.eprime {FILE_PATH}"


def modify_file(horizon_value):
    with open(FILE_PATH, "r", encoding="utf-8") as file:
        lines = file.readlines()

    with open(FILE_PATH, "w", encoding="utf-8") as file:
        for line in lines:
            if line.startswith("letting horizon = "):
                file.write(f"letting horizon = {horizon_value}\n")
            else:
                file.write(line)


_, _, cost = sa_procedure()

print(f"Updating HORIZON to {cost}")
modify_file(cost)

print(f"Running command: {TERMINAL_COMMAND}")

result = subprocess.run(
    TERMINAL_COMMAND,
    shell=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=False,
)

print(result.stdout.decode("utf-8"))
print(result.stderr.decode("utf-8"))
