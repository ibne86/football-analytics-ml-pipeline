import json
from pathlib import Path


input_file = Path("data/raw/fixtures_premier_league_2023.json")
output_file = Path("data/raw/fixtures_premier_league_2023_rows.jsonl")


with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)


fixtures = data["response"]


with open(output_file, "w", encoding="utf-8") as file:
    for fixture in fixtures:
        file.write(json.dumps(fixture) + "\n")


print(f"JSONL file created: {output_file}")
print(f"Number of fixture rows: {len(fixtures)}")