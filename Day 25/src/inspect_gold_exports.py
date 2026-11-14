from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"E:\Linkific\Day 25\data\gold_export")

TABLES = [
    "dim_region",
    "dim_customer",
    "dim_product",
    "dim_date",
    "fact_sales"
]

print("=" * 75)
print("DAY 24 - GOLD DATASET VALIDATION")
print("=" * 75)

for table in TABLES:
    table_dir = BASE_DIR / table
    csv_files = sorted(table_dir.glob("*.csv"))

    print(f"\n{'=' * 75}")
    print(f"TABLE: {table}")
    print("=" * 75)

    if not csv_files:
        print(f"ERROR: No CSV files found in {table_dir}")
        continue

    frames = []

    for file in csv_files:
        df_part = pd.read_csv(file)
        frames.append(df_part)
        print(f"File: {file.name} | Rows: {len(df_part)}")

    df = pd.concat(frames, ignore_index=True)

    print(f"\nTotal CSV files: {len(csv_files)}")
    print(f"Total rows: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nNull values:")
    print(df.isnull().sum())

    print("\nSample records:")
    print(df.head(3).to_string(index=False))

print("\n" + "=" * 75)
print("GOLD DATASET INSPECTION COMPLETED")
print("=" * 75)
