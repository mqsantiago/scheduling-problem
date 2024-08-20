import subprocess

# Define the terminal command you want to run
command = "time ../../../../Downloads/savilerow-1.10.0-linux/savilerow -sat -sat-family kissat -run-solver ../../../../Downloads/savilerow-1.10.0-linux/examples/mrcpsp-pb/mrcpsp-pb.eprime ../../../../Downloads/savilerow-1.10.0-linux/examples/mrcpsp-pb/j3060_1.param "
# command = "time python3 src/mrcpsp.py"

# Open the output file in write mode
with open("output.txt", "w") as output_file:
    for i in range(100):
        # Run the command and capture the output
        result = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Write the output to the file
        output_file.write(f"Run {i+1}:\n")
        output_file.write(result.stdout.decode("utf-8"))
        output_file.write(result.stderr.decode("utf-8"))
        output_file.write("\n" + "=" * 50 + "\n")
