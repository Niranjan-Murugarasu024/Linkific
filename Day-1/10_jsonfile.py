import json
from pathlib import Path

root = Path(__file__).resolve().parent
base_dir = root / "data"
input_file = base_dir / "config.json"
if not input_file.exists():
    input_file = base_dir / "raw" / "config.json"

output_file = base_dir / "processed" / "config_copy.json"
output_file.parent.mkdir(parents=True, exist_ok=True)

with input_file.open("r", encoding="utf-8") as file:
    config = json.load(file)

config["processed"] = True

with output_file.open("w", encoding="utf-8") as file:
    json.dump(config, file, indent=4)

print(config)