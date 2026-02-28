import json
import re
from collections import Counter


def analyze_news_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    news_texts = [item.get("news_text", "") for item in data["data"]]

    # Counter for exact line matches (to find recurring boilerplate)
    line_counter = Counter()

    # Counter for potential patterns
    html_tag_counter = Counter()

    # List to store sample "noisy" lines for manual inspection
    short_lines = []
    caps_lines = []

    total_lines = 0

    for text in news_texts:
        if not text:
            continue

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            total_lines += 1
            line_counter[line] += 1

            # Check for HTML tags
            tags = re.findall(r"<[^>]+>", line)
            for tag in tags:
                html_tag_counter[tag] += 1

            # Store some short lines (potential menu items)
            if len(line) < 20:
                short_lines.append(line)

            # Store all-caps lines (potential headers/noise)
            if line.isupper() and len(line) > 10:
                caps_lines.append(line)

    print(f"Total non-empty lines analyzed: {total_lines}")
    print("\n--- Top 20 Most Frequent Lines ---")
    for line, count in line_counter.most_common(20):
        print(f"{count}: {line}")

    print("\n--- Top 10 Detected HTML Tags ---")
    for tag, count in html_tag_counter.most_common(10):
        print(f"{count}: {tag}")

    print("\n--- Sample Short Lines (Potential Menu/Nav) ---")
    # Just print frequent short lines to avoid random noise
    short_line_counter = Counter(short_lines)
    for line, count in short_line_counter.most_common(20):
        print(f"{count}: {line}")

    print("\n--- Sample All-Caps Lines ---")
    caps_line_counter = Counter(caps_lines)
    for line, count in caps_line_counter.most_common(10):
        print(f"{count}: {line}")


if __name__ == "__main__":
    analyze_text_path = "dev.json"
    analyze_news_text(analyze_text_path)
