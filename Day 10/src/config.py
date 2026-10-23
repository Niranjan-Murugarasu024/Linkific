import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

def database_config() -> dict:
    required = ["PGHOST", "PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}. Copy .env.example to .env and configure it.")
    return {"host": os.getenv("PGHOST", "localhost"), "port": int(os.getenv("PGPORT", "5432")),
            "dbname": os.getenv("PGDATABASE", "ecommerce_practice"), "user": os.getenv("PGUSER", "postgres"),
            "password": os.getenv("PGPASSWORD")}

def sqlalchemy_url() -> str:
    from sqlalchemy.engine import URL
    c = database_config()
    return URL.create("postgresql+psycopg2", username=c["user"], password=c["password"],
                      host=c["host"], port=c["port"], database=c["dbname"])
