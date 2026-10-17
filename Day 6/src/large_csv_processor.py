from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
input_file = ROOT / "data" / "sales.csv"
output_file = ROOT / "reports" / "chunked_customer_revenue.csv"
output_file.parent.mkdir(parents=True, exist_ok=True)
partials = []
for chunk in pd.read_csv(input_file, chunksize=100_000):
    partials.append(chunk.groupby("customer_id")["revenue"].sum())
result = pd.concat(partials).groupby(level=0).sum().sort_values(ascending=False)
result.rename("total_revenue").to_csv(output_file)
print(f"Processed in chunks; output: {output_file}")
