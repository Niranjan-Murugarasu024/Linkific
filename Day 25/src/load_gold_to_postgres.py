
from pathlib import Path
import os
import sys

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "gold_export"

load_dotenv(PROJECT_DIR / ".env")


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "ecommerce_practice"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD"),
    "sslmode": os.getenv("PGSSLMODE", "prefer"),
}


SCHEMA = "day24_gold"

TABLES = [
    "dim_region",
    "dim_customer",
    "dim_product",
    "dim_date",
    "fact_sales",
]


# --------------------------------------------------
# 2. CSV READING
# --------------------------------------------------

def read_gold_table(table_name):
    folder = DATA_DIR / table_name
    files = sorted(folder.glob("*.csv"))

    if not files:
        raise FileNotFoundError(
            f"No CSV files found in {folder}"
        )

    frames = [pd.read_csv(file) for file in files]
    return pd.concat(frames, ignore_index=True)


# --------------------------------------------------
# 3. DATA QUALITY VALIDATION
# --------------------------------------------------

def validate_gold_data(data):
    primary_keys = {
        "dim_region": ["region_key"],
        "dim_customer": ["customer_key"],
        "dim_product": ["product_key"],
        "dim_date": ["date_key"],
        "fact_sales": ["order_id", "line_id"],
    }

    for table, columns in primary_keys.items():
        df = data[table]

        if df[columns].isnull().any().any():
            raise ValueError(
                f"NULL primary key found in {table}"
            )

        if df.duplicated(subset=columns).any():
            raise ValueError(
                f"Duplicate primary key found in {table}"
            )

    relationships = [
        ("dim_customer", "region_key", "dim_region", "region_key"),
        ("fact_sales", "customer_key", "dim_customer", "customer_key"),
        ("fact_sales", "product_key", "dim_product", "product_key"),
        ("fact_sales", "region_key", "dim_region", "region_key"),
        ("fact_sales", "date_key", "dim_date", "date_key"),
    ]

    for child_table, child_col, parent_table, parent_col in relationships:
        child_values = set(data[child_table][child_col].dropna())
        parent_values = set(data[parent_table][parent_col].dropna())

        missing = child_values - parent_values

        if missing:
            raise ValueError(
                f"Foreign key validation failed: "
                f"{child_table}.{child_col} has "
                f"{len(missing)} unmatched values. "
                f"Examples: {list(missing)[:5]}"
            )

    print("\nAll primary key and foreign key checks passed.")


# --------------------------------------------------
# 4. POSTGRESQL DDL
# --------------------------------------------------

DDL = """
CREATE SCHEMA IF NOT EXISTS day24_gold;

CREATE TABLE IF NOT EXISTS day24_gold.dim_region (
    region_key INTEGER PRIMARY KEY,
    region_id INTEGER NOT NULL,
    region_name VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS day24_gold.dim_customer (
    customer_key INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    customer_name VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    region_key INTEGER NOT NULL,
    CONSTRAINT fk_customer_region
        FOREIGN KEY (region_key)
        REFERENCES day24_gold.dim_region(region_key)
);

CREATE TABLE IF NOT EXISTS day24_gold.dim_product (
    product_key INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS day24_gold.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS day24_gold.fact_sales (
    order_id BIGINT NOT NULL,
    line_id INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    product_key INTEGER NOT NULL,
    region_key INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(14,2) NOT NULL,
    discount_pct NUMERIC(8,4) NOT NULL,
    gross_amount NUMERIC(16,2) NOT NULL,
    discount_amount NUMERIC(16,2) NOT NULL,
    net_amount NUMERIC(16,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    CONSTRAINT pk_fact_sales
        PRIMARY KEY (order_id, line_id),

    CONSTRAINT fk_sales_customer
        FOREIGN KEY (customer_key)
        REFERENCES day24_gold.dim_customer(customer_key),

    CONSTRAINT fk_sales_product
        FOREIGN KEY (product_key)
        REFERENCES day24_gold.dim_product(product_key),

    CONSTRAINT fk_sales_region
        FOREIGN KEY (region_key)
        REFERENCES day24_gold.dim_region(region_key),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date_key)
        REFERENCES day24_gold.dim_date(date_key)
);
"""


# --------------------------------------------------
# 5. CSV TO POSTGRESQL COLUMN MAPPING
# --------------------------------------------------

COLUMNS = {
    "dim_region": [
        "region_key", "region_id", "region_name", "country"
    ],
    "dim_customer": [
        "customer_key", "customer_id", "customer_name",
        "email", "region_key"
    ],
    "dim_product": [
        "product_key", "product_id", "product_name",
        "category", "unit_price"
    ],
    "dim_date": [
        "date_key", "full_date", "year", "quarter",
        "month", "month_name", "day"
    ],
    "fact_sales": [
        "order_id", "line_id", "customer_key", "product_key",
        "region_key", "date_key", "quantity", "unit_price",
        "discount_pct", "gross_amount", "discount_amount",
        "net_amount", "status", "updated_at"
    ],
}


# --------------------------------------------------
# 6. LOAD DATA USING POSTGRESQL COPY
# --------------------------------------------------

def load_table(cursor, table_name):
    folder = DATA_DIR / table_name
    files = sorted(folder.glob("*.csv"))

    columns = COLUMNS[table_name]

    for file_path in files:
        copy_query = sql.SQL(
            "COPY {}.{} ({}) "
            "FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
        ).format(
            sql.Identifier(SCHEMA),
            sql.Identifier(table_name),
            sql.SQL(", ").join(
                sql.Identifier(column) for column in columns
            ),
        )

        with open(file_path, "r", encoding="utf-8", newline="") as file:
            cursor.copy_expert(
                copy_query.as_string(cursor),
                file
            )

        print(f"Loaded: {table_name} <- {file_path.name}")


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():
    print("=" * 65)
    print("DAY 24 - GOLD TO POSTGRESQL ETL")
    print("=" * 65)

    if not DB_CONFIG["password"]:
        raise ValueError(
            "DB_PASSWORD is missing from the project .env file."
        )

    # Read all datasets
    data = {}

    for table in TABLES:
        data[table] = read_gold_table(table)
        print(f"{table}: {len(data[table])} rows")

    # Validate before connecting
    validate_gold_data(data)

    connection = None

    try:
        connection = psycopg2.connect(**DB_CONFIG)
        connection.autocommit = False

        with connection.cursor() as cursor:
            print("\nCreating PostgreSQL schema and tables...")
            cursor.execute(DDL)

            # All five tables are truncated together so their
            # foreign key dependencies remain valid.
            print("\nPreparing tables for reload...")
            cursor.execute("""
                TRUNCATE TABLE
                    day24_gold.fact_sales,
                    day24_gold.dim_customer,
                    day24_gold.dim_product,
                    day24_gold.dim_region,
                    day24_gold.dim_date;
            """)

            # Load dimensions before fact
            load_order = [
                "dim_region",
                "dim_customer",
                "dim_product",
                "dim_date",
                "fact_sales",
            ]

            print("\nLoading Gold datasets...")

            for table in load_order:
                load_table(cursor, table)

            # Verify PostgreSQL counts before commit
            print("\nPostgreSQL row-count verification:")

            for table in TABLES:
                cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                        sql.Identifier(SCHEMA),
                        sql.Identifier(table)
                    )
                )

                db_count = cursor.fetchone()[0]
                source_count = len(data[table])

                print(
                    f"{table}: source={source_count}, "
                    f"postgresql={db_count}"
                )

                if db_count != source_count:
                    raise ValueError(
                        f"Row count mismatch in {table}"
                    )

        connection.commit()

        print("\n" + "=" * 65)
        print("GOLD DATA SUCCESSFULLY LOADED INTO POSTGRESQL")
        print(f"Database: {DB_CONFIG['dbname']}")
        print(f"Schema: {SCHEMA}")
        print("=" * 65)

    except Exception:
        if connection:
            connection.rollback()

        print("\nETL FAILED. Transaction rolled back.")
        raise

    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
