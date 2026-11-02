"""Clean customer CSV data and export validation/extraction reports."""
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.validators import validate_email, validate_phone
from patterns.regex_patterns import SPECIAL_CHAR_PATTERN, WHITESPACE_PATTERN

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "raw" / "customers.csv"
OUTPUT_DIR = ROOT / "data" / "processed"

DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d")

def clean_name(value):
    value = WHITESPACE_PATTERN.sub(" ", str(value).strip())
    value = re.sub(r"[^A-Za-z '\\-]", "", value)
    return value.title()

def clean_email(value):
    return str(value).strip().lower()

def clean_phone(value):
    digits = "".join(re.findall(r"\d", str(value)))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    return digits

def clean_date(value):
    value = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def clean_address(value):
    value = SPECIAL_CHAR_PATTERN.sub("", str(value).strip())
    return WHITESPACE_PATTERN.sub(" ", value)

def clean_customer_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input not found: {INPUT_FILE}. Run `python main.py` to generate sample data.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(INPUT_FILE, dtype={"Phone": "string"})
    df["Name"] = df["Name"].fillna("").apply(clean_name)
    df["Email"] = df["Email"].fillna("").apply(clean_email)
    df["Phone"] = df["Phone"].fillna("").apply(clean_phone)
    df["Date"] = df["Date"].fillna("").apply(clean_date)
    df["Address"] = df["Address"].fillna("").apply(clean_address)

    df["Valid_Email"] = df["Email"].apply(validate_email)
    df["Valid_Phone"] = df["Phone"].apply(validate_phone)
    df["Valid_Date"] = df["Date"].notna()
    df["Valid_Record"] = df["Valid_Email"] & df["Valid_Phone"] & df["Valid_Date"]

    df.to_csv(OUTPUT_DIR / "cleaned_customers.csv", index=False)
    df[["CustomerID", "Email"]].to_csv(OUTPUT_DIR / "extracted_emails.csv", index=False)
    df[["CustomerID", "Phone"]].to_csv(OUTPUT_DIR / "extracted_phones.csv", index=False)

    print(f"Customer records processed: {len(df)}")
    print(f"Valid records: {int(df['Valid_Record'].sum())}")
    print(f"Invalid records: {int((~df['Valid_Record']).sum())}")
    print(f"Reports saved to: {OUTPUT_DIR}")
    return df
