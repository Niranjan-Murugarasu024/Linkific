import time
from src.monitoring.logger import get_logger

logger = get_logger()


def run_with_retry(operation, attempts=3, base_delay_seconds=1):
    """Retry transient operations with exponential backoff; re-raise final failure."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(1, attempts + 1):
        try:
            return operation()
        except Exception:
            logger.exception("Operation failed on attempt %s/%s", attempt, attempts)
            if attempt == attempts:
                raise
            time.sleep(base_delay_seconds * (2 ** (attempt - 1)))
