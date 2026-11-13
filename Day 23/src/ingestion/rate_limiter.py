import time
class RateLimiter:
    # Process-local minimum-interval limiter; not intended for distributed workers.
    def __init__(self, requests_per_second=2):
        if requests_per_second <= 0: raise ValueError("Rate must be positive")
        self.interval, self.last = 1/requests_per_second, 0
    def wait(self):
        delay = self.interval - (time.monotonic()-self.last)
        if delay > 0: time.sleep(delay)
        self.last = time.monotonic()
