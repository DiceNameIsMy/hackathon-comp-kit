import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TARGET_INDEX = 4  # Constant index to select a single object. Must have > 0 claims.


def main():
    json_path = "dev.json"

    # Check if file exists
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        sys.exit(1)

    # Load data
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}.")
        sys.exit(1)

    # Validate index
    if TARGET_INDEX < 0 or TARGET_INDEX >= len(data["data"]):
        print(f"Error: Index {TARGET_INDEX} out of range.")
        sys.exit(1)

    # Get object
    obj = data["data"][TARGET_INDEX]
    target_claims = obj.get("target_number_of_claims", 0)
    source_text = obj.get("source", "")

    # Check claims count
    if target_claims == 0:
        print(
            f"Error: The target number of claims is 0 for index {TARGET_INDEX}. Exiting."
        )
        sys.exit(1)

    print(f"Processing Index: {TARGET_INDEX}")
    print(f"Source Text: {source_text[:100]}...")
    print(f"Target Claims: {target_claims}")

    # Prepare prompt based on eda.ipynb style but adapted for extraction
    prompt = f"""
Identify the factual claims in the **given comment**.

## Goal
Extract exactly {target_claims} verifiable factual claim(s) from the comment.

## Instructions
1. Read the comment carefully.
2. Identify independent factual claims that can be verified.
3. Select the {target_claims} most significant claims that match the intent of the speaker.
4. List exactly {target_claims} claim(s).

## Output format
- Provide a numbered list of exactly {target_claims} claim(s).
- Do not include any introductory or concluding text.
"""

    # Call LLM
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Using the specific client method from eda.ipynb
        # Note: 'responses.create' is used as per the notebook example, assuming a custom environment wrapper.
        response = client.responses.create(
            model="gpt-5.2",
            reasoning=None,
            instructions=prompt,
            input=source_text,
        )

        print("\n--- Extracted Claims ---")
        print(response.output_text)

    except Exception as e:
        print(f"Error calling LLM: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
