import importlib
import os
from dotenv import load_dotenv

load_dotenv()

INSTANCE_NAME = os.getenv("PROBLEM_INSTANCE")

current_instance = importlib.import_module(f"instances.{INSTANCE_NAME}")


def worst_time_scenario(instance):
    return sum(max(d) for d in instance.DURATIONS)


print(
    f"Worst time scenario for {INSTANCE_NAME}: {worst_time_scenario(current_instance)}"
)
