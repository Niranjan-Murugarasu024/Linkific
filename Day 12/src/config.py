import logging
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

load_dotenv(ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
API_URL = os.getenv(
    "API_URL",
    "https://dummyjson.com/products"
)

API_PAGE_SIZE = int(os.getenv("API_PAGE_SIZE", "30"))
API_MAX_PAGES = int(os.getenv("API_MAX_PAGES", "100"))

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging():
    logger = logging.getLogger("etl_pipeline")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        LOG_DIR / "pipeline.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()