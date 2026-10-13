
import json
from pathlib import Path

import pandas as pd

from api_client import get_data

# creates the folder structure
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def save_data(name, data):
    # Save the original API response.
    raw_file = RAW_DIR / f"{name}.json"
    raw_file.write_text(
        json.dumps(data, indent=2),
        encoding="utf-8"
    )

    # Convert the records to a DataFrame.
    if isinstance(data, dict):
        records = data.get("posts", data.get("products", data.get("data", [])))
    else:
        records = data

    if records and isinstance(records, list):
        df = pd.json_normalize(records)
        df.to_csv(
            PROCESSED_DIR / f"{name}.csv",
            index=False,
            encoding="utf-8-sig"
        )
        print(f"{name}: saved {len(df)} records")
    else:
        print(f"{name}: no records found in the expected format")


def main():
    apis = {
        "posts": "https://jsonplaceholder.typicode.com/posts",
        "products": "https://dummyjson.com/products?limit=30",
        "users": "https://jsonplaceholder.typicode.com/users",
    }

    for name, url in apis.items():
        try:
            print(f"Fetching {name}...")
            data = get_data(url)
            save_data(name, data)
        except (requests.RequestException, ValueError) as error:
            print(f"{name} failed: {error}")


if __name__ == "__main__":
    import requests
    main()