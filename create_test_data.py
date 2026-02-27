import json

with open("dev.json", "r") as f:
    data = json.load(f)

data["data"] = data["data"][:10]

with open("dev_test.json", "w") as f:
    json.dump(data, f, indent=2)

print("Created dev_test.json with 10 samples.")
