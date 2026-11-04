import argparse, os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

TABLES = [
    ("ecommerce_customers","ecommerce_customers.csv"), ("ecommerce_products","ecommerce_products.csv"),
    ("ecommerce_orders","ecommerce_orders.csv"), ("ecommerce_order_items","ecommerce_order_items.csv"),
    ("ecommerce_payments","ecommerce_payments.csv"), ("hr_departments","hr_departments.csv"),
    ("hr_employees","hr_employees.csv"), ("hr_attendance","hr_attendance.csv"), ("hr_payroll","hr_payroll.csv"),
    ("finance_customers","finance_customers.csv"), ("finance_accounts","finance_accounts.csv"),
    ("finance_transactions","finance_transactions.csv")
]
def main():
    load_dotenv()
    parser=argparse.ArgumentParser()
    parser.add_argument("--database", default=os.getenv("PGDATABASE","synthetic_lab"))
    parser.add_argument("--data", default=os.getenv("DATA_DIR","data/generated"))
    args=parser.parse_args()
    conn=psycopg2.connect(host=os.getenv("PGHOST","localhost"), port=os.getenv("PGPORT","5432"),
        user=os.getenv("PGUSER","postgres"), password=os.getenv("PGPASSWORD",""), dbname=args.database)
    with conn, conn.cursor() as cur:
        cur.execute(Path("sql/schema.sql").read_text(encoding="utf-8"))
        for table, filename in TABLES:
            path=Path(args.data)/filename
            if not path.exists(): raise FileNotFoundError(path)
            cur.execute(f'TRUNCATE TABLE "{table}" CASCADE')
            with path.open("r", encoding="utf-8") as f:
                cur.copy_expert(f'COPY "{table}" FROM STDIN WITH CSV HEADER', f)
            print(f"Loaded {table}: {path.stat().st_size:,} bytes")
    conn.close()
if __name__=="__main__":
    main()
