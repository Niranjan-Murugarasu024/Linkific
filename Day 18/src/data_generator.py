"""Generate reproducible sample customer and application-log files."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

CUSTOMERS = [
    ["CustomerID", "Name", "Email", "Phone", "Date", "Address"],
    [1, " Niranjan ", "NIRANJAN@GMAIL.COM", "+91 9876543210", "12/05/2025", "Coimbatore, TN"],
    [2, "John Smith", "john@gmail.com", "98765-43210", "2025-06-15", "Chennai, TN"],
    [3, "Priya@123", "priya@gmail.com", "9876543211", "15-07-2025", "Madurai, TN"],
    [4, "Arun Kumar", "arun.gmail.com", "1234567890", "2025/08/20", "Salem, TN"],
    [5, " Meena ", "meena@yahoo.com", "+91-8765432109", "01/09/2025", "Erode, TN"],
    [6, "Robert", "robert@outlook.com", "87654 32109", "2025-10-10", "Bangalore, KA"],
    [7, "Karthik", "karthik@gmail.com", "9876543212", "31-11-2025", "Chennai, TN"],
    [8, "Anitha", "anitha@@gmail.com", "99999-11111", "2025-12-01", "Trichy, TN"],
    [9, "Vijay", "vijay@gmail.com", "+91 9123456789", "05/01/2026", "Coimbatore, TN"],
    [10, "David", "david@yahoo.com", "8123456789", "2026-02-15", "Hyderabad, TS"],
]

LOGS = [
    "2026-11-02 09:15:20 INFO 192.168.1.10 User login successful",
    "2026-11-02 09:16:30 ERROR 192.168.1.20 Payment failed ORD-123456",
    "2026-11-02 09:17:40 WARNING 192.168.1.30 High memory usage",
    "2026-11-02 09:18:50 INFO 192.168.1.40 Order completed ORD-654321",
    "2026-11-02 09:19:10 CRITICAL 192.168.1.50 Database connection failed",
    "2026-11-02 09:20:10 DEBUG 192.168.1.60 Request received",
    "INVALID LOG ENTRY",
    "2026-11-02 09:21:10 ERROR 999.999.999.999 Invalid IP example",
]

def generate_sample_data():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with (RAW_DIR / "customers.csv").open("w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(CUSTOMERS)
    (RAW_DIR / "application.log").write_text("\n".join(LOGS) + "\n", encoding="utf-8")
    print(f"Created sample data in: {RAW_DIR}")

if __name__ == "__main__":
    generate_sample_data()
