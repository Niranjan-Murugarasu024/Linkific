from pathlib import Path
import requests
from src.utils.error_handler import retry
from src.utils.logger import get_logger
log = get_logger("api")

RAW = Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)

@retry(attempts=3)
def get_json(url, params=None):
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    return response.json()

def collect_apis():
    sources = {
        "jsonplaceholder_users": "https://jsonplaceholder.typicode.com/users",
        "dummyjson_products": "https://dummyjson.com/products",
        "restcountries": "https://restcountries.com/v3.1/all?fields=name,cca2,region,population",
    }
    results = {}
    for name, url in sources.items():
        data = get_json(url)
        # DummyJSON wraps records in its "products" field.
        if isinstance(data, dict) and "products" in data:
            data = data["products"]
        results[name] = data
        (RAW / f"{name}.json").write_text(__import__("json").dumps(data, indent=2), encoding="utf-8")
        log.info("Collected %s records from %s", len(data) if isinstance(data, list) else 1, name)
    return results
