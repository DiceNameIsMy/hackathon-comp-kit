import json
import sys

# IDs to process
target_ids = [
    "Q29tbWVudE5vZGU6Mjk1Mjc4NDIz",
    "1194921",
    "6282093803",
    "1708487",
    "6182425551",
]

try:
    with open("dev_checkworthy.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    found_samples = []

    # Check if data is a list or a dict with 'data' key
    if isinstance(data, dict) and "data" in data:
        items = data["data"]
    elif isinstance(data, list):
        items = data
    else:
        print("Unknown JSON format")
        sys.exit(1)

    for item in items:
        if str(item.get("id")) in target_ids:
            found_samples.append(item)

    # Print found samples as JSON
    print(json.dumps(found_samples, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
