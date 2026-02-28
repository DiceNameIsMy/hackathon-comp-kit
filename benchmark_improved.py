import subprocess
import json
import time
import os
import sys
import statistics

IDS = [
    "Q29tbWVudE5vZGU6Mjk1Mjc4NDIz",
    "1194921",
    "6282093803",
]

CONFIGS = {
    "Baseline": [],
    "Clean": ["-clean"],
    "Keywords": ["-experimental"],
    "Both": ["-clean", "-experimental"],
}

ITERATIONS = 3
MODEL = "inception"  # Or "inception" if desired
PYTHON_EXEC = ".venv/bin/python"
RESULTS_FILE = "comparison_results.json"
REPORT_FILE = "benchmark_report.md"


def run_benchmark():
    overall_results = {}

    print(
        f"Starting benchmark on {len(IDS)} IDs with {len(CONFIGS)} configurations, {ITERATIONS} iterations each."
    )

    for sample_id in IDS:
        overall_results[sample_id] = {}
        print(f"\nProcessing ID: {sample_id}")

        for config_name, flags in CONFIGS.items():
            scores = []
            print(f"  Configuration: {config_name}...", end="", flush=True)

            for i in range(ITERATIONS):
                cmd = [
                    PYTHON_EXEC,
                    "main.py",
                    "-id",
                    sample_id,
                    "-judge",
                    "-model",
                    MODEL,
                ] + flags

                try:
                    result = subprocess.run(
                        cmd, capture_output=True, text=True, check=True
                    )

                    # Read the last entry from results file
                    if not os.path.exists(RESULTS_FILE):
                        print("Error: Results file not found.")
                        continue

                    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if not data:
                            print("Error: Results file empty.")
                            continue
                        last_entry = data[-1]

                        # Verify ID matches (sanity check)
                        if last_entry.get("id") != sample_id:
                            print(
                                f"Warning: Last entry ID mismatch! Expected {sample_id}, got {last_entry.get('id')}"
                            )

                        score = last_entry.get("judge_score", "N/A")
                        try:
                            score_val = float(score)
                            scores.append(score_val)
                        except ValueError:
                            pass  # Score is N/A or invalid

                except subprocess.CalledProcessError as e:
                    print(f"Error running command: {e}")
                    print(e.stderr)
                except Exception as e:
                    print(f"Unexpected error: {e}")

            avg_score = statistics.mean(scores) if scores else 0
            overall_results[sample_id][config_name] = avg_score
            print(f" Done. Avg Score: {avg_score:.2f}")

    generate_report(overall_results)


def generate_report(results):
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# Benchmark Report: Clean & Keywords Features\n\n")
        f.write(f"Model: {MODEL}\n")
        f.write(f"Iterations per config: {ITERATIONS}\n\n")

        # Summary Table
        f.write("## Summary by ID\n\n")
        f.write("| ID | Baseline | Clean | Keywords | Both |\n")
        f.write("|---|---|---|---|---|\n")

        config_names = ["Baseline", "Clean", "Keywords", "Both"]

        # Calculate totals for averages
        totals = {name: [] for name in config_names}

        for sample_id in IDS:
            row = f"| {sample_id} |"
            for name in config_names:
                score = results[sample_id].get(name, 0)
                row += f" {score:.2f} |"
                totals[name].append(score)
            f.write(row + "\n")

        f.write("\n## Overall Averages\n\n")
        f.write("| Configuration | Average Score |\n")
        f.write("|---|---|\n")
        for name in config_names:
            avg = statistics.mean(totals[name]) if totals[name] else 0
            f.write(f"| {name} | {avg:.2f} |\n")

    print(f"\nBenchmark complete. Report saved to {REPORT_FILE}")
    subprocess.run(["cat", REPORT_FILE])


if __name__ == "__main__":
    run_benchmark()
