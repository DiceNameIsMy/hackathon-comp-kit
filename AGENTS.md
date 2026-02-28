# Operational Guidelines

- Always use the python environment located at `.venv/bin`.

# Project Overview

This repository contains a tool for analyzing and verifying claims found in comments against news articles. The core logic involves breaking down comments into atomic claims ("atomization") and then providing context for those claims based on the article ("decontextualization").

## Core Component: `main.py`

`main.py` is the primary entry point for the pipeline. It orchestrates the following steps:

1.  **Data Loading:** Reads samples (comments + articles) from a JSON file (default: `dev_checkworthy.json`).
2.  **Atomization:** Uses an LLM to split a comment into individual, verifiable claims.
3.  **Decontextualization:** Uses an LLM (and optionally keyword-based filtering) to rewrite claims with necessary context from the article.
4.  **Judgment (Optional):** Compares the generated claims against a ground truth set to score the performance.

### Usage

The script is run via the CLI. Common arguments include:

-   `-count <int>`: Number of random samples to process (default: 1).
-   `-id <str>`: Process a specific sample by its ID.
-   `-model <openai|inception>`: Select the LLM provider (default: openai).
-   `-experimental`: Enable experimental keyword-based context filtering for long articles.
-   `-judge`: Run the LLM judge to evaluate the output quality.
-   `-clean`: Pre-process and clean the news text.
-   `-verbose`: Print detailed prompts and raw model outputs to the console.

**Example:**
```bash
# Process 5 random samples using the experimental context strategy and run the judge
python main.py -count 5 -experimental -judge
```

## Directory Structure

-   `prompts/`: Contains Markdown files with the prompt templates for different stages (atomize, decontext, judge, etc.).
-   `data/`: Directory containing input datasets and analysis outputs.
