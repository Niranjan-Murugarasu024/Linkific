from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
base_dir = root / "data"
log_file = base_dir / "sample.txt"
if not log_file.exists():
    log_file = base_dir / "raw" / "sample.txt"

counts = Counter()

with log_file.open("r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()

        if ":" not in line:
            counts["UNCLASSIFIED"] += 1
            continue

        level, _message = line.split(":", maxsplit=1)
        counts[level.strip()] += 1

print("Log summary:")

for level, count in counts.items():
    print(f"{level}: {count}")