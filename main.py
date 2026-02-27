import requests
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

with open("dev_checkworthy.json", "r") as f:
    data = json.load(f)["data"]

with open("atomize.md", "r", encoding="utf-8") as f:
    CLAIM_SEP = f.read()


with open("decontext.md", "r", encoding="utf-8") as f:
    DECONTEXT = f.read()


def send_prompt_to_inception(prompt):
    response = requests.post(
        "https://api.inceptionlabs.ai/v1/chat/completions",
        headers={
            "Authorization": "Bearer xxx",
            "Content-Type": "application/json",
        },
        json={
            "model": "mercury-2",
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    return response.json()


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def send_prompt_to_openai(prompt):
    response = client.responses.create(
        model="gpt-5.2",
        reasoning=None,
        instructions=None,
        input=prompt,
    )
    return response


def decontextualize(article, message):
    input = DECONTEXT.replace("[ARTICLE]", article).replace("[MESSAGE]", message)
    response = send_prompt_to_openai(input)
    output = response.output_text.split("UVAŽOVÁNÍ: ")[-1]
    reasoning, d = output.split("DEKONTEX: ")
    return d, reasoning, response.output_text


def atomize(message, expected_claims: int):
    input = CLAIM_SEP.replace("[TVRZENÍ]", message)
    output = send_prompt_to_openai(input).output_text
    lines = output.splitlines()
    atoms = []
    reasonings = []
    for line in lines:
        if line.startswith("ATOM: "):
            atom = line.split(": ", 1)[-1]
            atoms.append(atom)
        elif line.startswith("UVAŽOVÁNÍ: "):
            reasoning = line.split(": ", 1)[-1]
            reasonings.append(reasoning)
    
    return atoms, reasonings



def print_readable(text):
    for i in range(0, len(text), 80):
        print(text[i : i + 80])


def decontextualize_then_atomize(article, comment, expected_claims: int):
    if article == "":
        print("WARN: No article provided, using placeholder.")
        article = "<No article provided, return the message as is.>"

    d, reasoning, doutput = decontextualize(article, comment)

    print_readable(d)
    aoutput = atomize(d, expected_claims)

    return d, reasoning, doutput, aoutput


if __name__ == "__main__":
    idx = 5
    article = data[idx]["news_text"]
    comment = data[idx]["source"]
    expected_claims = len(data[idx]["claims"])

    atoms, reasonings = atomize(comment, expected_claims)
    for a, z in zip(atoms, reasonings):
        print("ATOM: ", a)
        print("ATOM_REASONING: ", z)

        d, reasoning, doutput = decontextualize(article, a)
        print("DECONT: ", d)
        print("DECONT_REASONING: ", reasoning)
        print()


    # d, reasoning, doutput, aoutput = decontextualize_then_atomize(
    #     article,
    #     comment,
    #     expected_claims,
    # )

    # print(aoutput.output_text)

    # print_readable(data[4]["source"])
