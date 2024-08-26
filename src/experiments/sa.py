import subprocess
import os

from dotenv import load_dotenv

load_dotenv()


def print_env():
    instance_name = os.getenv("PROBLEM_INSTANCE")

    chains = int(os.getenv("CHAINS", "3"))
    steps = int(os.getenv("STEPS", "5"))
    neighbours_initial_n = int(os.getenv("NEIGHBOURS_INITIAL_N", "1000"))
    neighbours_increase_coefficient = int(
        os.getenv("NEIGHBOURS_INCREASE_COEFFICIENT", "1")
    )
    temperature_max = int(os.getenv("TEMPERATURE_MAX", "100"))
    temperature_increase_coefficient = float(
        os.getenv("TEMPERATURE_INCREASE_COEFFICIENT", "0.25")
    )

    print(f"Instance: {instance_name}")
    print(f"Chains: {chains}")
    print(f"Steps: {steps}")
    print(f"Neighbours Initial N: {neighbours_initial_n}")
    print(f"Neighbours Increase Coefficient: {neighbours_increase_coefficient}")
    print(f"Temperature Max: {temperature_max}")
    print(f"Temperature Increase Coefficient: {temperature_increase_coefficient}\n")


COMMAND = "time python3 src/main.py"

print_env()

for i in range(100):
    result = subprocess.run(
        COMMAND,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    print(f"Run {i+1}:\n")
    print(result.stdout.decode("utf-8"))
    print(result.stderr.decode("utf-8"))
    print("\n" + "=" * 50 + "\n")
