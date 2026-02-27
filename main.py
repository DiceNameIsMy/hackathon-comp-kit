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
    return send_prompt_to_openai(input)


def atomize(article, message, expected_claims: int):
    input = (
        CLAIM_SEP.replace("[ARTICLE]", article)
        .replace("[COMMENT]", message)
        .replace("[N]", str(expected_claims))
    )
    return send_prompt_to_openai(input)


def print_readable(text):
    for i in range(0, len(text), 80):
        print(text[i : i + 80])


def decontextualize_then_atomize(article, comment, expected_claims: int):
    if article == "":
        print("WARN: No article provided, using placeholder.")
        article = "<No article provided, return the message as is.>"

    doutput = decontextualize(article, comment)
    d = doutput.output_text.split("\n")[-1]
    print_readable(d)

    aoutput = atomize(doutput.output_text, d, expected_claims)

    return d, doutput, aoutput


if __name__ == "__main__":
    idx = 4
    d, doutput, aoutput = decontextualize_then_atomize(
        data[idx]["news_text"],
        data[idx]["source"],
        len(data[idx]["claims"]),
    )

    print(aoutput.output_text)

    print_readable(data[4]["source"])
