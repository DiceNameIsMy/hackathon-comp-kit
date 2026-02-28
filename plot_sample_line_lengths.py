import json
import matplotlib.pyplot as plt
import sys
import os
import argparse
from clean_text import clean_news_text


def main():
    parser = argparse.ArgumentParser(description="Plot line lengths of a news sample.")
    parser.add_argument(
        "index", nargs="?", type=int, default=0, help="Index of the sample (default: 0)"
    )
    parser.add_argument("--id", help="Target ID of the sample")
    parser.add_argument(
        "--clean", action="store_true", help="Clean the article text before plotting"
    )

    args = parser.parse_args()

    target_id = args.id
    index = args.index
    clean = args.clean

    # Use absolute paths relative to the script location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "dev.json")

    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    if target_id:
        print(f"Loading data for sample ID {target_id}...")
    else:
        print(f"Loading data for sample index {index}...")

    with open(path, "r", encoding="utf-8") as f:
        content = json.load(f)

    data = content["data"]

    sample = None
    if target_id:
        for i, item in enumerate(data):
            if str(item.get("id")) == str(target_id):
                sample = item
                index = i
                break
        if sample is None:
            print(f"Error: Sample with ID {target_id} not found.")
            return
    else:
        if index < 0 or index >= len(data):
            print(f"Error: Index {index} is out of range (0 to {len(data) - 1})")
            return
        sample = data[index]

    text = sample.get("news_text", "")

    if clean:
        print("Cleaning text...")
        text = clean_news_text(text)

    if not text:
        print("Warning: 'news_text' is empty for this sample.")
        lines = []
        lengths = []
    else:
        lines = text.split("\n")
        lengths = [len(line) for line in lines]

    print(f"Sample ID: {sample.get('id', 'N/A')}")
    print(f"Source: {sample.get('source', 'N/A')}")
    if not clean:
        print(f"Match original: {sample.get('news_text') == text}")
    print("-" * 20)
    print(text[:500])
    print("-" * 20)
    # print(lines[:30])

    print(f"Number of lines: {len(lengths)}")

    plt.figure(figsize=(12, 6))

    # Using a bar plot to visualize the text structure
    plt.bar(range(len(lengths)), lengths, width=0.8, color="steelblue")

    plt.xlabel("Line Number")
    plt.ylabel("Line Length (characters)")

    title = f"Line Lengths for Sample {index} (ID: {sample.get('id', 'N/A')})"
    if clean:
        title += " (Cleaned)"
    plt.title(title)

    plt.grid(axis="y", alpha=0.3)

    output_dir = os.path.join(base_dir, "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filename_suffix = "_cleaned" if clean else ""
    output_file = os.path.join(
        output_dir,
        f"sample_{sample.get('id', index)}_line_lengths{filename_suffix}.png",
    )

    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")


if __name__ == "__main__":
    main()
