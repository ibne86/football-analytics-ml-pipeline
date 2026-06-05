import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")

if not API_KEY:
    raise ValueError("FOOTBALL_API_KEY is missing. Please add it to your .env file.")


BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

endpoint = f"{BASE_URL}/fixtures"

params = {
    "league": 39,
    "season": 2023
}

response = requests.get(endpoint, headers=headers, params=params, timeout=30)

print("Status code:", response.status_code)

data = response.json()

print("Number of results:", data.get("results"))

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / "fixtures_premier_league_2023.json"

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2)

print(f"Data saved to {output_file}")