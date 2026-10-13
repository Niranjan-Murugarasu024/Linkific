import csv
from pathlib import Path

root = Path(__file__).resolve().parent
base_dir = root / "data"
input_file = base_dir / "jan_sales.csv"
if not input_file.exists():
    input_file = base_dir / "raw" / "sales_january.csv"

output_file = base_dir / "processed" / "sales_cleaned.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)

with input_file.open("r", encoding="utf-8", newline="") as source:
    reader = csv.DictReader(source)
    rows = list(reader)

for row in rows:
    row["amount"] = float(row["amount"])
    row["order_id"] = int(row["order_id"])

with output_file.open("w", encoding="utf-8", newline="") as destination:
    writer = csv.DictWriter(
        destination,
        fieldnames=["order_id", "customer", "amount", "order_date"],
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Processed {len(rows)} rows")