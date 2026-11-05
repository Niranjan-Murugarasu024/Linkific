import time
from functools import wraps
from src.utils.logger import get_logger
log = get_logger("retry")

def retry(attempts=3, delay=1):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for attempt in range(1, attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:
                    last = exc
                    log.exception("Attempt %s/%s failed: %s", attempt, attempts, exc)
                    if attempt < attempts:
                        time.sleep(delay * attempt)
            raise last
        return wrapper
    return decorator
