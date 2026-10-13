import csv
from pathlib import Path

root = Path(__file__).resolve().parent
base_dir = root / "data"
raw_dir = base_dir / "raw"
source_dir = raw_dir if raw_dir.exists() else base_dir
output_file = base_dir / "output" / "all_sales.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)

fieldnames = ["order_id", "customer", "amount", "order_date"]
total_rows = 0

with output_file.open("w", encoding="utf-8", newline="") as destination:
    writer = csv.DictWriter(destination, fieldnames=fieldnames)
    writer.writeheader()

    candidates = sorted(source_dir.glob("sales_*.csv"))
    if not candidates:
        candidates = sorted(source_dir.glob("*sales*.csv"))
    if not candidates:
        candidates = [
            path for path in sorted(source_dir.glob("*.csv"))
            if "sales" in path.stem.lower()
        ]

    for source_file in candidates:
        with source_file.open("r", encoding="utf-8", newline="") as source:
            reader = csv.DictReader(source)

            if reader.fieldnames != fieldnames:
                raise ValueError(f"Unexpected columns in {source_file.name}")

            for row in reader:
                writer.writerow(row)
                total_rows += 1

print(f"Combined {total_rows} rows into {output_file.name}")