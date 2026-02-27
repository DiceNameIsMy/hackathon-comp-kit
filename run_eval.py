#!/usr/bin/env python3
"""
Minimal evaluation script for FDM hackathon competitors.
Loads data from a JSON file, runs your task1/task2 predictor on each example,
and adds checkworthy_prediction (task1) or claims_prediction (task2) to each item.
Output is the full input structure plus modified data and your team_token from .env.

Usage:
  python run_eval.py data/fdm/dev.json task1
  python run_eval.py data/fdm/dev.json task2 -o submission.json
"""
import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
import os

from task1 import run_task1
from task2 import run_task2


def load_full_data(path: Path) -> dict:
    """Load the full JSON structure (dict with 'data' key or similar)."""
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"data": data}
    raise ValueError(f"Expected JSON object or array in {path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run task1 (checkworthiness) and/or task2 (claims) on a JSON data file."
    )
    parser.add_argument(
        "data_path",
        type=Path,
        help="Path to data JSON, e.g. data/fdm/dev.json",
    )
    parser.add_argument(
        "task",
        choices=["task1", "task2"],
        help="Which task to run: task1 or task2",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output JSON file (default: out_task1.json, out_task2.json, or out_both.json by task)",
    )
    args = parser.parse_args()
    return args


def main() -> None:
    load_dotenv()
    args = parse_args()

    # Validate arguments
    if args.output is None:
        args.output = Path(f"out_{args.task}.json")

    if not args.data_path.exists():
        print(f"Error: file not found: {args.data_path}", file=sys.stderr)
        sys.exit(1)

    team_token = os.environ.get("TEAM_TOKEN", "").strip()
    if not team_token:
        print("Error: TEAM_TOKEN not set. Create a .env file with TEAM_TOKEN=your-token", file=sys.stderr)
        sys.exit(1)

    # Load data
    payload = load_full_data(args.data_path)
    examples = payload.get("data")
    if not isinstance(examples, list):
        print("Error: input JSON must contain a 'data' key with a list of examples", file=sys.stderr)
        sys.exit(1)

    # Run your inference
    for example in examples:
        if args.task == "task1":
            example["checkworthy_prediction"] = run_task1(example)
        else:
            # Skip claim extraction for non-checkworthy claims
            if example['checkworthy']:
                example["claims_prediction"] = run_task2(example)

    # Add team-token & save data
    payload["team_token"] = team_token
    payload["eval_task"] = args.task
    text = json.dumps(payload, ensure_ascii=False, indent=2)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
