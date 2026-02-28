import argparse
import random
import json
import os
import requests
import re
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from clean_text import clean_news_text

load_dotenv()

# Constants
DATA_PATH = "dev_checkworthy.json"
ATOMIZE_PROMPT_PATH = "prompts/atomize.md"
DECONTEXT_PROMPT_PATH = "prompts/decontext.md"
KEYWORDS_PROMPT_PATH = "prompts/decontext_keywords.md"
JUDGE_PROMPT_PATH = "prompts/judge.md"
EXPERIMENTAL_MIN_LENGTH = 1000

console = Console()


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


def print_verbose_step(title, prompt, response):
    console.print(f"[bold cyan]--- VERBOSE: {title} ---[/bold cyan]")
    console.print("[dim]PROMPT:[/dim]")
    console.print(Text(prompt, style="dim"))
    console.print("[dim]RESPONSE:[/dim]")
    console.print(Text(response, style="dim"))
    console.print(
        f"[bold cyan]-------------------------{'-' * len(title)}----[/bold cyan]\n"
    )


def atomize(
    message, atomize_template, expected_count, model_name="openai", verbose=False
):
    prompt = atomize_template.replace("[TVRZENÍ]", message).replace(
        "[COUNT]", str(expected_count)
    )
    output = get_model_response(prompt, model_name)

    if verbose:
        print_verbose_step("ATOMIZE", prompt, output)

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
    verbose=False,
):
    context_used = "Full Article"
    if experimental and len(article) > EXPERIMENTAL_MIN_LENGTH:
        # Step 1: Identify keywords
        keyword_prompt = keywords_template.replace("[MESSAGE]", atom)
        keywords_output = get_model_response(keyword_prompt, model_name)

        if verbose:
            print_verbose_step(
                "KEYWORDS (Experimental)", keyword_prompt, keywords_output
            )

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
            context_used = "Filtered Context"
        else:
            context = article
    else:
        context = article

    # Step 3: Decontextualize using context (filtered or full)
    prompt = decontext_template.replace("[ARTICLE]", context).replace("[MESSAGE]", atom)
    output = get_model_response(prompt, model_name)

    if verbose:
        print_verbose_step("DECONTEXTUALIZE", prompt, output)

    decont = output.strip()
    if "DEKONTEX: " in output:
        decont = output.split("DEKONTEX: ")[-1].strip()
    return decont, output, context_used


def judge_output(
    source_text,
    article_context,
    generated_claims,
    expected_claims,
    judge_template,
    model_name="openai",
    verbose=False,
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
    output = get_model_response(prompt, model_name)

    if verbose:
        print_verbose_step("JUDGE", prompt, output)

    return output


def parse_judge_result(judge_text):
    score = "N/A"
    explanation = judge_text

    # Simple regex to extract score and explanation if format matches
    score_match = re.search(r"SKÓRE:\s*(\d+)", judge_text, re.IGNORECASE)
    if score_match:
        score = score_match.group(1)

    expl_match = re.split(r"VYSVĚTLENÍ:\s*", judge_text, flags=re.IGNORECASE)
    if len(expl_match) > 1:
        explanation = expl_match[1].strip()

    return score, explanation


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
    parser.add_argument(
        "-verbose",
        action="store_true",
        help="Show detailed prompt inputs and raw outputs",
    )
    args = parser.parse_args()

    data = load_data(args.file)
    if not isinstance(data, list):
        console.print(
            "[bold red]Error: Input file must contain a list of samples (or 'data' key with a list).[/bold red]"
        )
        return
    atomize_template, decontext_template, keywords_template, judge_template = (
        load_prompts()
    )

    if args.id:
        sample = next((item for item in data if item.get("id") == args.id), None)
        if sample:
            samples = [sample]
        else:
            console.print(f"[bold red]Sample with ID '{args.id}' not found.[/bold red]")
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

        # Header for the sample
        console.print(
            Panel(
                f"[bold]Source Comment:[/bold]\n{comment}\n\n[dim]ID: {sample.get('id', 'N/A')}[/dim]",
                title=f"Sample {idx + 1}/{len(samples)}",
                border_style="blue",
            )
        )

        expected_count = len(sample.get("claims", []))

        with console.status("[bold green]Atomizing comment...[/bold green]"):
            atoms, atomize_raw = atomize(
                comment, atomize_template, expected_count, args.model, args.verbose
            )

        decont_outputs = []
        decont_raw_outputs = []

        # Create a table for processing steps
        table = Table(
            title="Claim Processing", show_header=True, header_style="bold magenta"
        )
        table.add_column("Original Atom", style="cyan", width=30)
        table.add_column("Context Strategy", style="dim", width=15)
        table.add_column("Decontextualized Result", style="green")

        for atom in atoms:
            with console.status(
                f"[bold green]Decontextualizing: {atom[:20]}...[/bold green]"
            ):
                decont, decont_raw, context_used = decontextualize(
                    article,
                    atom,
                    decontext_template,
                    keywords_template,
                    args.experimental,
                    args.model,
                    args.verbose,
                )
            decont_outputs.append(decont)
            decont_raw_outputs.append(decont_raw)
            table.add_row(atom, context_used, decont)

        console.print(table)

        # Expected Claims Display
        exp_table = Table(title="Expected Ground Truth", show_header=False, box=None)
        exp_table.add_column("Claim", style="italic")
        for claim in expected_claims:
            exp_table.add_row(f"✓ {claim}")
        console.print(exp_table)

        judge_res = None
        judge_score = "N/A"
        judge_explanation = ""

        if args.judge:
            with console.status(
                "[bold yellow]Running Judge Assessment...[/bold yellow]"
            ):
                judge_res = judge_output(
                    comment,
                    article,
                    decont_outputs,
                    expected_claims,
                    judge_template,
                    args.model,
                    args.verbose,
                )

            judge_score, judge_explanation = parse_judge_result(judge_res)

            # Formatting Judge Output
            score_color = (
                "green" if judge_score.isdigit() and int(judge_score) >= 7 else "red"
            )

            judge_panel = Panel(
                f"[bold]Explanation:[/bold]\n{judge_explanation}",
                title=f"Judge Assessment - Score: [{score_color}]{judge_score}/10[/{score_color}]",
                border_style="yellow",
            )
            console.print(judge_panel)

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
                "judge_score": judge_score,
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

    console.print(
        f"\n[bold green]Processed {len(samples)} samples. Results appended to {output_file}[/bold green]"
    )


if __name__ == "__main__":
    main()
