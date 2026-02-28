import json


def create_checkworthy_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    checkworthy_items = [
        item for item in data["data"] if item.get("checkworthy") is True
    ]

    output_data = {"split": data.get("split", "dev"), "data": checkworthy_items}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Created {output_path} with {len(checkworthy_items)} items.")


if __name__ == "__main__":
    create_checkworthy_file("dev_cleaned.json", "dev_cleaned_checkworthy.json")
