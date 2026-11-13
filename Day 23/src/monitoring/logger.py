import logging, os
from pathlib import Path

def get_logger(name="day23"):
    Path("logs").mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
        for handler in (logging.FileHandler("logs/ingestion.log", encoding="utf-8"), logging.StreamHandler()):
            handler.setFormatter(fmt)
            logger.addHandler(handler)
    return logger
