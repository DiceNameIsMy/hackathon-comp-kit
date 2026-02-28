import json

with open("dev_checkworthy.json", "r") as f:
    data = json.load(f)["data"]

for item in data:
    if len(item.get("news_text", "")) > 2000:
        print(f"ID: {item['id']}, Length: {len(item['news_text'])}")
        print(f"Text Snippet: {item['news_text'][:100]}...")
        break
