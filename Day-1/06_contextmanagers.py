from pathlib import Path

root = Path(__file__).resolve().parent
file_path = root / "data" / "sample.txt"

file_path.parent.mkdir(parents=True, exist_ok=True)

with file_path.open("w", encoding="utf-8") as file:
    file.write("Python data engineering\n")
    file.write("Context managers simplify resource handling\n")

with file_path.open("r", encoding="utf-8") as file:
    content = file.read()

print(content)