from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
input_file = reports / "enriched_sales.csv"
if not input_file.exists():
    raise FileNotFoundError("Run `python src/merge_datasets.py` first.")
df = pd.read_csv(input_file, parse_dates=["order_date"])
summary = pd.DataFrame({"metric": ["Total revenue", "Orders", "Units sold"],
                        "value": [df["revenue"].sum(), df["sale_id"].nunique(), df["quantity"].sum()]})
by_region = df.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), orders=("sale_id", "nunique"))
monthly = df.assign(month=df["order_date"].dt.to_period("M").astype(str)).groupby("month", as_index=False)["revenue"].sum()
output = reports / "sales_business_report.xlsx"
with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
    summary.to_excel(writer, sheet_name="Executive Summary", index=False, startrow=1)
    by_region.to_excel(writer, sheet_name="By Region", index=False)
    monthly.to_excel(writer, sheet_name="Monthly Trend", index=False)
    df.to_excel(writer, sheet_name="Sales Detail", index=False)
    workbook = writer.book
    header = workbook.add_format({"bold": True, "bg_color": "#D9EAF7", "border": 1})
    money = workbook.add_format({"num_format": '"₹"#,##0.00'})
    for name, frame in [("Executive Summary", summary), ("By Region", by_region),
                        ("Monthly Trend", monthly), ("Sales Detail", df)]:
        ws = writer.sheets[name]
        header_row = 1 if name == "Executive Summary" else 0
        ws.freeze_panes(header_row + 1, 0)
        for i, col in enumerate(frame.columns):
            ws.write(header_row, i, col, header)
            ws.set_column(i, i, min(max(len(col) + 3, 12), 28))
        ws.autofilter(header_row, 0, header_row + len(frame), len(frame.columns)-1)
    for name, frame in [("By Region", by_region), ("Monthly Trend", monthly), ("Sales Detail", df)]:
        writer.sheets[name].set_column(frame.columns.get_loc("revenue"), frame.columns.get_loc("revenue"), 16, money)
print(f"Created {output}")
