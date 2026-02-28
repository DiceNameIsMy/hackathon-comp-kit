import subprocess
import time

ids = [
    "Q29tbWVudE5vZGU6Mjk1Mjc4NDIz",
    "1194921",
    "6282093803",
    "1708487",
    "6182425551",
    "6268829774",
    "Q29tbWVudE5vZGU6MjU5Mjc4ODM0",
    "69497",
    "10548389",
    "34367085",
]

output_file = "benchmark_results.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Benchmark Run - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 50 + "\n\n")

for i, sample_id in enumerate(ids):
    print(f"Running sample {i + 1}/{len(ids)}: {sample_id}")
    try:
        start_time = time.time()
        # Run main.py with the sample ID and model
        result = subprocess.run(
            [
                ".venv/bin/python",
                "main.py",
                "-id",
                sample_id,
                "-model",
                "inception",
                "-clean",
                "-experimental",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
        duration = time.time() - start_time

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"--- Benchmark Sample {i + 1} (ID: {sample_id}) ---\n")
            f.write(f"Execution Time: {duration:.2f}s\n")

            if result.returncode == 0:
                f.write(result.stdout)
            else:
                f.write(f"ERROR (Return Code {result.returncode}):\n")
                f.write(result.stderr)
                f.write(result.stdout)

            f.write("\n" + "=" * 50 + "\n\n")

    except Exception as e:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"CRITICAL ERROR running sample {sample_id}: {str(e)}\n\n")

print(f"Benchmark complete. Results saved to {output_file}")
