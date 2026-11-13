from urllib.parse import urljoin
from bs4 import BeautifulSoup
from src.collectors.api_collector import APICollector
from src.monitoring.logger import get_logger
log = get_logger(__name__)

def scrape_books(url, max_pages=2):
    client, rows = APICollector(), []
    for page in range(max_pages):
        response = client.session.get(url, timeout=client.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select("article.product_pod"):
            title = item.select_one("h3 a")
            price = item.select_one(".price_color")
            avail = item.select_one(".availability")
            rows.append({
                "title": title.get("title") if title else None,
                "price": price.get_text(strip=True) if price else None,
                "availability": avail.get_text(" ", strip=True) if avail else None,
                "source_url": urljoin(url, title.get("href")) if title else url
            })
        log.info("Scraped page=%d total=%d", page + 1, len(rows))
        nxt = soup.select_one("li.next a")
        if not nxt: break
        url = urljoin(url, nxt.get("href"))
    return rows
