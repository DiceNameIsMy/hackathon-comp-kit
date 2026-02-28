import argparse
import random
import json
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
from clean_text import clean_news_text

load_dotenv()

# Constants
DATA_PATH = "dev_checkworthy.json"
ATOMIZE_PROMPT_PATH = "atomize.md"
DECONTEXT_PROMPT_PATH = "decontext.md"
KEYWORDS_PROMPT_PATH = "decontext_keywords.md"
JUDGE_PROMPT_PATH = "judge.md"
EXPERIMENTAL_MIN_LENGTH = 1000


def load_data(file_path):
    with open(file_path, "r") as f:
        content = json.load(f)
        if isinstance(content, dict) and "data" in content:
            return content["data"]
        return content


def load_prompts():
    with open(ATOMIZE_PROMPT_PATH, "r", encoding="utf-8") as f:
        atomize_prompt = f.read()
    with open(DECONTEXT_PROMPT_PATH, "r", encoding="utf-8") as f:
        decontext_prompt = f.read()
    with open(KEYWORDS_PROMPT_PATH, "r", encoding="utf-8") as f:
        keywords_prompt = f.read()
    with open(JUDGE_PROMPT_PATH, "r", encoding="utf-8") as f:
        judge_prompt = f.read()
    return atomize_prompt, decontext_prompt, keywords_prompt, judge_prompt


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


def get_model_response(prompt, model_name):
    if model_name == "inception":
        response = send_prompt_to_inception(prompt)
        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return str(response)
    else:
        # OpenAI
        response = send_prompt_to_openai(prompt)
        return response.output_text


def atomize(message, atomize_template, expected_count, model_name="openai"):
    prompt = atomize_template.replace("[TVRZENÍ]", message).replace(
        "[COUNT]", str(expected_count)
    )
    output = get_model_response(prompt, model_name)
    lines = output.splitlines()
    atoms = []
    for line in lines:
        if line.startswith("ATOM: "):
            atoms.append(line.split(": ", 1)[-1])
    return atoms, output


def decontextualize(
    article,
    atom,
    decontext_template,
    keywords_template,
    experimental=False,
    model_name="openai",
):
    if experimental and len(article) > EXPERIMENTAL_MIN_LENGTH:
        # Step 1: Identify keywords
        keyword_prompt = keywords_template.replace("[MESSAGE]", atom)
        keywords_output = get_model_response(keyword_prompt, model_name)

        # Parse keywords (assuming comma-separated)
        keywords = [k.strip() for k in keywords_output.split(",")]

        # Step 2: Filter sentences
        sentences = article.replace("\n", " ").split(". ")
        filtered_sentences = []
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                filtered_sentences.append(sentence)

        # If filtering failed to find anything (e.g., keywords not found or empty), fallback to full article
        if filtered_sentences:
            context = ". ".join(filtered_sentences)
        else:
            context = article
    else:
        context = article

    # Step 3: Decontextualize using context (filtered or full)
    prompt = decontext_template.replace("[ARTICLE]", context).replace("[MESSAGE]", atom)
    output = get_model_response(prompt, model_name)

    decont = output.strip()
    if "DEKONTEX: " in output:
        decont = output.split("DEKONTEX: ")[-1].strip()
    return decont, output


def judge_output(
    source_text,
    article_context,
    generated_claims,
    expected_claims,
    judge_template,
    model_name="openai",
):
    full_source = f"Tvrzení: {source_text}\n\nKontext: {article_context}"
    # Truncate context if too long? Not handling for now.
    prompt = judge_template.replace("[SOURCE]", full_source)
    prompt = prompt.replace(
        "[GENERATED]", "\n".join([f"- {c}" for c in generated_claims])
    )
    prompt = prompt.replace(
        "[EXPECTED]", "\n".join([f"- {c}" for c in expected_claims])
    )
    return get_model_response(prompt, model_name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-count", type=int, default=1, help="Number of random samples to process"
    )
    parser.add_argument("-id", type=str, help="Specific sample ID to process")
    parser.add_argument(
        "-model",
        type=str,
        default="openai",
        choices=["openai", "inception"],
        help="Model to use: openai or inception",
    )
    parser.add_argument(
        "-file",
        type=str,
        default=DATA_PATH,
        help="Path to input JSON file",
    )
    parser.add_argument(
        "-clean",
        action="store_true",
        help="Clean the news text before processing",
    )
    parser.add_argument(
        "-experimental",
        action="store_true",
        help="Use experimental decontextualization with keyword filtering",
    )
    parser.add_argument(
        "-judge",
        action="store_true",
        help="Run LLM judge to assess the result",
    )
    args = parser.parse_args()

    data = load_data(args.file)
    atomize_template, decontext_template, keywords_template, judge_template = (
        load_prompts()
    )

    if args.id:
        sample = next((item for item in data if item.get("id") == args.id), None)
        if sample:
            samples = [sample]
        else:
            print(f"Sample with ID '{args.id}' not found.")
            return
    else:
        samples = random.sample(data, min(args.count, len(data)))
    results = []

    for idx, sample in enumerate(samples):
        article = sample.get("news_text", "")
        if args.clean:
            article = clean_news_text(article)
        comment = sample.get("source", "")
        expected_claims = sample.get("claims", [])

        print(f"\n--- Sample {idx + 1} (ID: {sample.get('id', 'N/A')}) ---")
        print(f"Source: {comment[:100]}...")

        expected_count = len(sample.get("claims", []))
        atoms, atomize_raw = atomize(
            comment, atomize_template, expected_count, args.model
        )
        decont_outputs = []
        decont_raw_outputs = []

        for atom in atoms:
            decont, decont_raw = decontextualize(
                article,
                atom,
                decontext_template,
                keywords_template,
                args.experimental,
                args.model,
            )
            decont_outputs.append(decont)
            decont_raw_outputs.append(decont_raw)
            print(f"DECONT: {decont}")

        print("Expected Claims:")
        for claim in expected_claims:
            print(f"EXPECTED: {claim}")

        judge_res = None
        if args.judge:
            print("\nRunning Judge Assessment...")
            judge_res = judge_output(
                comment,
                article,
                decont_outputs,
                expected_claims,
                judge_template,
                args.model,
            )
            print(f"JUDGE:\n{judge_res}")

        results.append(
            {
                "id": sample.get("id"),
                "source": comment,
                "atoms": atoms,
                "atomize_raw": atomize_raw,
                "decont_outputs": decont_outputs,
                "decont_raw_outputs": decont_raw_outputs,
                "expected_claims": expected_claims,
                "judge_evaluation": judge_res,
                "model": args.model,
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
