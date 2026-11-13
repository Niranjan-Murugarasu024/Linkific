import os, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from src.monitoring.logger import get_logger

log = get_logger(__name__)

class APICollector:
    def __init__(self):
        retry = Retry(total=int(os.getenv("MAX_RETRIES", "3")), connect=3, read=3, status=3,
                      backoff_factor=0.7, status_forcelist=[429,500,502,503,504],
                      allowed_methods=["GET"], respect_retry_after_header=True)
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.headers["User-Agent"] = "Day23IngestionFramework/1.0"
        token = os.getenv("DEMO_API_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        self.timeout = int(os.getenv("REQUEST_TIMEOUT", "20"))

    def get_json(self, url, params=None):
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        try:
            return response.json()
        except ValueError as exc:
            raise ValueError(f"Invalid JSON from {response.url}") from exc

    def jsonplaceholder(self, cfg):
        rows, page, size = [], 1, int(cfg.get("page_size", 10))
        while True:
            batch = self.get_json(cfg["base_url"] + cfg["endpoint"], {"_page": page, "_limit": size})
            if not batch: break
            rows.extend(batch)
            log.info("JSONPlaceholder page=%d rows=%d", page, len(batch))
            if len(batch) < size: break
            page += 1
        return rows

    def dummyjson(self, cfg):
        rows, skip, size = [], 0, int(cfg.get("page_size", 10))
        while True:
            data = self.get_json(cfg["base_url"] + cfg["endpoint"], {"limit": size, "skip": skip})
            batch = data.get("products", [])
            if not batch: break
            rows.extend(batch); skip += len(batch)
            log.info("DummyJSON skip=%d rows=%d", skip, len(batch))
            if skip >= int(data.get("total", skip)): break
        return rows

    def countries(self, cfg):
        return self.get_json(cfg["base_url"] + cfg["endpoint"], {"fields": cfg.get("fields", "name,cca2,region")})
