import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parent
base_dir = root / "data"
input_file = base_dir / "jan_sales.csv"
if not input_file.exists():
    input_file = base_dir / "raw" / "sales_january.csv"

output_file = base_dir / "output" / "sales_report.xlsx"
output_file.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)

df["amount"] = pd.to_numeric(df["amount"], errors="raise")
df["order_date"] = pd.to_datetime(df["order_date"], errors="raise")

summary = (
    df.groupby("customer", as_index=False)["amount"]
    .sum()
    .rename(columns={"amount": "total_sales"})
)

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Sales", index=False)
    summary.to_excel(writer, sheet_name="Summary", index=False)

print(f"Excel report created: {output_file}")