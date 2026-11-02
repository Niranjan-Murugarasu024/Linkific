"""Parse structured application logs and validate extracted IPv4 addresses."""
import ipaddress
from pathlib import Path
import pandas as pd

from patterns.regex_patterns import LOG_LINE_PATTERN, ORDER_ID_PATTERN

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "raw" / "application.log"
OUTPUT_FILE = ROOT / "data" / "processed" / "parsed_logs.csv"

def parse_log_file():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Log file not found: {INPUT_FILE}. Run `python main.py` first.")

    records = []
    skipped = 0
    for line_number, raw_line in enumerate(INPUT_FILE.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        match = LOG_LINE_PATTERN.fullmatch(line)
        if not match:
            print(f"Skipping malformed log line {line_number}")
            skipped += 1
            continue
        data = match.groupdict()
        try:
            ipaddress.IPv4Address(data["ip"])
        except ipaddress.AddressValueError:
            print(f"Skipping invalid IP at log line {line_number}: {data['ip']}")
            skipped += 1
            continue
        order_ids = ORDER_ID_PATTERN.findall(data["message"])
        records.append({
            "Timestamp": data["timestamp"],
            "Log_Level": data["level"],
            "IP_Address": data["ip"],
            "Message": data["message"],
            "Order_ID": order_ids[0] if order_ids else None,
        })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records, columns=["Timestamp", "Log_Level", "IP_Address", "Message", "Order_ID"])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Parsed log records: {len(df)}")
    print(f"Skipped log lines: {skipped}")
    if not df.empty:
        print("\nLog-level summary:")
        print(df["Log_Level"].value_counts().to_string())
    print(f"Log report saved to: {OUTPUT_FILE}")
    return df
