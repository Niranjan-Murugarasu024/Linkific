from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent

print("Project root:", project_root)
print("Current timestamp:", datetime.now().isoformat())