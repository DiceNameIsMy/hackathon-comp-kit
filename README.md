# FDM Hackathon – Competitor evaluation kit

Standalone script to run your checkworthiness (task1) and claims extraction (task2) models on the dev/eval data and produce a submission JSON.

## Setup

1. **Copy the environment file and set your token**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set `TEAM_TOKEN` to the token you received from the organisers.

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   (Only `python-dotenv` is required.)

## Usage

```bash
python run_eval.py <data_path> <task> [-o output.json]
```

- **data_path** – Path to the data JSON (e.g. `data/fdm/dev.json`).
- **task** – `task1` (checkworthiness), `task2` (claims), or `both`.
- **-o, --output** – Output JSON file. Defaults: `out_task1.json`, `out_task2.json`, or `out_both.json` depending on `task`.

### Examples

```bash
# Task 1 only → writes out_task1.json
python run_eval.py data/fdm/dev.json task1

# Task 2 only → writes out_task2.json
python run_eval.py data/fdm/dev.json task2

# Both tasks → writes out_both.json, or use -o to choose the file
python run_eval.py data/fdm/dev.json both -o submission.json
```

## Input and output

- **Input**: A JSON file with a top-level **`data`** key containing a list of examples. Each example has at least `source` (text) and an id field (`original_id` or `comment_id`). Any other top-level keys in the file are preserved.

- **Output**: The **full input structure** is kept (all keys and nesting). The script only:
  - Updates the **`data`** list by adding to each example:
    - **task1**: `checkworthy_prediction` (boolean)
    - **task2**: `claims_prediction` (list of strings)
  - Adds **`team_token`** at the top level (loaded from `.env`).

So if the input is e.g. `{"data": [...], "split": "dev"}`, the output will be `{"data": [modified items], "split": "dev", "team_token": "..."}`.

## Implementing your model

Edit `run_eval.py` and implement:

- **`run_task1(example)`** – Return a `bool`: whether the `example` is checkworthy. Use `example["source"]` (and optionally `original_id` / `comment_id`).

- **`run_task2(example)`** – Return a list of claim strings extracted from `example["source"]`.

The script calls these for each item in `data` and writes the result (with `team_token`) to the output file. Submit the produced JSON via the evaluation server’s upload form.
# hackathon-comp-kit
