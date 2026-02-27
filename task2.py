import os
import re
import json
import yaml
import requests
from time import sleep


def run_task2(example: dict) -> list:
    """
    Automatic claim extraction using a two-step LLM approach.
    1. Decompose text into all possible claims.
    2. Filter for checkworthy claims.
    """
    # --- Configuration & Setup ---
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback to simple split if no API key is present to prevent crashes
        text = example.get("source", "")
        return [text[i:i + 50] for i in range(0, len(text), 50)]

    model = "claude-3-7-sonnet-latest"
    prompt_path = "prompt.yaml"

    # Load prompts from external yaml
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            decompose_prompt = data["decompose_prompt"]
            checkworthy_prompt = data["checkworthy_prompt"]
    except (FileNotFoundError, KeyError):
        return ["Error: prompt.yaml missing or invalid"]

    # --- Helper Functions (Internalized) ---
    def call_anthropic(user_text: str):
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "max_tokens": 2800,
            "messages": [{"role": "user", "content": user_text}]
        }
        r = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=100)
        r.raise_for_status()
        data = r.json()
        return "".join(p.get("text", "") for p in data.get("content", []) if p.get("type") == "text").strip()

    def parse_json_content(text: str):
        match = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL)
        clean_text = match.group(1).strip() if match else text.strip()
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            return {}

    # --- Extraction Logic ---
    source_text = example.get("source", "").strip()
    if not source_text:
        return []

    # Attempt to get 'num_claims' if your dataset provides a target count, otherwise default
    num_claims_str = str(example.get("num_claims", "5"))

    max_retries = 3
    final_claims = []

    for attempt in range(max_retries):
        try:
            # Step 1: Decomposition
            decomp_resp = call_anthropic(decompose_prompt.format(doc=source_text, num_checkworthy=num_claims_str))
            obj_decomp = parse_json_content(decomp_resp)
            all_claims = [c.strip() for c in obj_decomp.get("claims", []) if isinstance(c, str) and c.strip()]

            if not all_claims:
                continue

            # Step 2: Checkworthiness Filtering
            numbered_claims = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(all_claims))
            check_resp = call_anthropic(
                checkworthy_prompt.format(texts=numbered_claims, num_checkworthy=num_claims_str))
            obj_check = parse_json_content(check_resp)

            # Extract claims where the value starts with "ano" (Czech for "yes")
            final_claims = [c for c, v in obj_check.items() if isinstance(v, str) and v.lower().startswith("ano")]

            if final_claims:
                break

            sleep(2)  # Brief pause before retry
        except Exception as e:
            print(f"Extraction attempt {attempt} failed: {e}")
            continue

    return final_claims