from pathlib import Path

root = Path(__file__).resolve().parent
data_dir = root / "data"

for path in data_dir.iterdir():
    if path.is_file():
        print(
            f"Name: {path.name} | "
            f"Extension: {path.suffix} | "
            f"Size: {path.stat().st_size} bytes"
        )

csv_files = list(data_dir.glob("*.csv"))
print("CSV files:", [path.name for path in csv_files])