import argparse
import random
import json
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Constants
DATA_PATH = "dev_checkworthy.json"
ATOMIZE_PROMPT_PATH = "atomize.md"
DECONTEXT_PROMPT_PATH = "decontext.md"


def load_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)["data"]


def load_prompts():
    with open(ATOMIZE_PROMPT_PATH, "r", encoding="utf-8") as f:
        atomize_prompt = f.read()
    with open(DECONTEXT_PROMPT_PATH, "r", encoding="utf-8") as f:
        decontext_prompt = f.read()
    return atomize_prompt, decontext_prompt


# Custom client setup as per existing main.py
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def send_prompt_to_inception(prompt):
    response = requests.post(
        "https://api.inceptionlabs.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('INCEPTION_API_KEY')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "mercury-2",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return response.json()


def send_prompt_to_openai(prompt):
    # Maintaining the specific structure used in the original script
    response = client.responses.create(
        model="gpt-5.2",
        reasoning=None,
        instructions=None,
        input=prompt,
    )
    return response


def atomize(message, atomize_template):
    prompt = atomize_template.replace("[TVRZENÍ]", message)
    response = send_prompt_to_openai(prompt)
    output = response.output_text
    lines = output.splitlines()
    atoms = []
    for line in lines:
        if line.startswith("ATOM: "):
            atoms.append(line.split(": ", 1)[-1])
    return atoms, output


def decontextualize(article, atom, decontext_template):
    prompt = decontext_template.replace("[ARTICLE]", article).replace("[MESSAGE]", atom)
    response = send_prompt_to_openai(prompt)
    output = response.output_text

    decont = output.strip()
    if "DEKONTEX: " in output:
        decont = output.split("DEKONTEX: ")[-1].strip()
    return decont, output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-count", type=int, default=1, help="Number of random samples to process"
    )
    args = parser.parse_args()

    data = load_data()
    atomize_template, decontext_template = load_prompts()

    samples = random.sample(data, min(args.count, len(data)))
    results = []

    for idx, sample in enumerate(samples):
        article = sample.get("news_text", "")
        comment = sample.get("source", "")
        expected_claims = sample.get("claims", [])

        print(f"\n--- Sample {idx + 1} (ID: {sample.get('id', 'N/A')}) ---")
        print(f"Source: {comment[:100]}...")

        atoms, atomize_raw = atomize(comment, atomize_template)
        decont_outputs = []
        decont_raw_outputs = []

        for atom in atoms:
            decont, decont_raw = decontextualize(article, atom, decontext_template)
            decont_outputs.append(decont)
            decont_raw_outputs.append(decont_raw)
            print(f"DECONT: {decont}")

        print(f"Expected Claims: {expected_claims}")

        results.append(
            {
                "id": sample.get("id"),
                "source": comment,
                "atoms": atoms,
                "atomize_raw": atomize_raw,
                "decont_outputs": decont_outputs,
                "decont_raw_outputs": decont_raw_outputs,
                "expected_claims": expected_claims,
            }
        )

    # Store results
    output_file = "comparison_results.json"
    existing_results = []
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                existing_results = json.load(f)
                if not isinstance(existing_results, list):
                    existing_results = []
        except (json.JSONDecodeError, IOError):
            existing_results = []

    existing_results.extend(results)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_results, f, indent=2, ensure_ascii=False)

    print(f"\nProcessed {len(samples)} samples. Results appended to {output_file}")


if __name__ == "__main__":
    main()
