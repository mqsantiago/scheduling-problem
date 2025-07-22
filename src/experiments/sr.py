import subprocess

INSTANCES = [
    # ("j3011_9", "30"),
    # ("j3012_4", "30"),
    # ("j3022_4", "30"),
    # ("j3025_10", "30"),
    # ("j3031_8", "30"),
    # ("j3055_8", "30"),
    # ("j3058_7", "30"),
    # ("j3059_5", "30"),
    # ("j3060_1", "30"),
    # ("j3063_7", "30"),
    # ("J50107_4", "50"),
    # ("J50103_2", "50"),
    # ("J5023_1", "50"),
    # ("J5028_1", "50"),
    # ("J5036_2", "50"),
    # ("J5039_3", "50"),
    # ("J5059_2", "50"),
    # ("J5076_1", "50"),
    # ("J5089_4", "50"),
    # ("J5090_1", "50"),
    # ("J10010_1", "100"),
    ("J100107_2", "100"),
    # ("J10021_5", "100"),
    # ("J10023_4", "100"),
    # ("J10028_3", "100"),
    # ("J10032_5", "100"),
    # ("J10039_1", "100"),
    # ("J10052_1", "100"),  # 1
    # ("J10063_3", "100"),
    # ("J10078_4", "100"),
]

FILE_PATH = "src/helpers/sr"

BASE = "../../../../Downloads/savilerow-1.10.0-linux"

MODIFIERS = "-sat -amo-detect -sat-family kissat -run-solver"

TERMINAL_COMMAND = f"timeout 1h time {BASE}/savilerow {MODIFIERS} {BASE}/examples/mrcpsp-pb/mrcpsp-pb.eprime {FILE_PATH}"


for instance in INSTANCES:
    print("\n" + "=" * 50 + "\n")
    print("\n" + "=" * 50 + "\n")

    print(f"NEW INSTANCE: {instance[0]}")

    N = 1

    if instance[0] == "NAN":
        N = 1

    for i in range(N):
        command = f"{TERMINAL_COMMAND}/{instance[1]}/{instance[0]}.param"
        print(command)

        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        print(f"Run {i+1}:\n")
        print(result.stdout.decode("utf-8"))
        print(result.stderr.decode("utf-8"))
        print("\n" + "=" * 50 + "\n")
