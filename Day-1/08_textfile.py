from pathlib import Path

root = Path(__file__).resolve().parent
input_file = root / "data"/ "sample.txt"
output_file = root / "data" / "info_log.txt"

output_file.parent.mkdir(parents=True, exist_ok=True)

with input_file.open("r", encoding="utf-8") as file:
    lines = file.readlines()

info_lines = [
    line for line in lines
    if line.startswith("INFO:")
]

with output_file.open("w", encoding="utf-8") as file:
    file.writelines(info_lines)

print(f"Read {len(lines)} lines")
print(f"Wrote {len(info_lines)} INFO lines")