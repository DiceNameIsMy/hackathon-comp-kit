import json

target_words = {"volby", "rozhovory", "velikost", "sport", "video"}

with open("dev.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data["data"]:
    text = item.get("news_text", "")
    if not text:
        continue
    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped in target_words:
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context = lines[start:end]
            print(f"--- Found '{stripped}' in item ---")
            for j, ctx_line in enumerate(context):
                prefix = ">> " if start + j == i else "   "
                print(f"{prefix}{ctx_line.strip()}")
            print("-" * 20)
