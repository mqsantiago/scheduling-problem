import subprocess

# List of HORIZON values to be used in the loop
horizon_values = [
    28,
    26,
    26,
    28,
    27,
    30,
    31,
    31,
    32,
    30,
    29,
    28,
    31,
    29,
    31,
    26,
    30,
    29,
    29,
    31,
    26,
    30,
    23,
    32,
    28,
    28,
    30,
    30,
    27,
    29,
    32,
    30,
    28,
    27,
    28,
    34,
    30,
    31,
    27,
    29,
    29,
    29,
    28,
    28,
    27,
    33,
    28,
    29,
    32,
    25,
    29,
    31,
    31,
    28,
    31,
    34,
    33,
    28,
    27,
    28,
    25,
    28,
    26,
    26,
    31,
    28,
    29,
    27,
    30,
    31,
    28,
    29,
    32,
    30,
    25,
    27,
    30,
    29,
    31,
    30,
    34,
    31,
    31,
    28,
    30,
    27,
    30,
    29,
    25,
    30,
    27,
    26,
    32,
    28,
    31,
    29,
    28,
    27,
    34,
    27,
]

# Path to the file that needs to be modified
file_path = (
    "../../../../Downloads/savilerow-1.10.0-linux/examples/mrcpsp-pb/j3060_1.param"
)

# Terminal command to be run after modifying the file
terminal_command = "time ../../../../Downloads/savilerow-1.10.0-linux/savilerow -sat -amo-detect -sat-family kissat -run-solver ../../../../Downloads/savilerow-1.10.0-linux/examples/mrcpsp-pb/mrcpsp-pb.eprime ../../../../Downloads/savilerow-1.10.0-linux/examples/mrcpsp-pb/j3060_1.param"


def modify_file(horizon_value):
    with open(file_path, "r") as file:
        lines = file.readlines()

    with open(file_path, "w") as file:
        for line in lines:
            if line.startswith("letting horizon = "):
                file.write(f"letting horizon = {horizon_value}\n")
            else:
                file.write(line)


def run_command():
    result = subprocess.run(
        terminal_command, shell=True, capture_output=True, text=True
    )
    return result.stdout, result.stderr


with open("output.txt", "w") as output_file:
    for i, value in enumerate(horizon_values):
        print(f"Updating HORIZON to {value}")
        modify_file(value)
        print(f"Running command: {terminal_command}")
        stdout, stderr = run_command()

        # Write the output to the file
        output_file.write(f"Run {i + 1} with value {value}:\n")
        output_file.write(stdout)
        output_file.write(stderr)
        output_file.write("\n" + "=" * 50 + "\n")
