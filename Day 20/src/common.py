from pathlib import Path
from faker import Faker
import csv, random
from datetime import date, datetime, timedelta

fake = Faker()
def seed_all(seed: int = 42):
    Faker.seed(seed)
    random.seed(seed)

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def write_csv(path, rows, fieldnames):
    ensure_dir(Path(path).parent)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def rand_date(start=date(2022,1,1), end=date(2026,10,31)):
    days = (end-start).days
    return start + timedelta(days=random.randint(0, max(days,0)))

def money(value):
    return round(float(value), 2)
