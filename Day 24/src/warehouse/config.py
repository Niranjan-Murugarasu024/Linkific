from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def database_config() -> dict:
    """Return PostgreSQL connection settings from environment variables."""
    required = ["PGDATABASE", "PGUSER", "PGPASSWORD"]
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            f"Missing environment setting(s): {', '.join(missing)}. "
            "Copy .env.example to .env and configure PostgreSQL credentials."
        )
    return {
        "host": os.getenv("PGHOST", "localhost"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.environ["PGDATABASE"],
        "user": os.environ["PGUSER"],
        "password": os.environ["PGPASSWORD"],
        "connect_timeout": int(os.getenv("PGCONNECT_TIMEOUT", "10")),
    }


def connect():
    try:
        import psycopg2
    except ImportError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError("Install dependencies first: pip install -r requirements.txt") from exc
    return psycopg2.connect(**database_config())
