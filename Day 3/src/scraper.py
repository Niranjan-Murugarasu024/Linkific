
import csv
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
OUTPUT_FILE = Path("data/raw/books_raw.csv")

HEADERS = {
    "User-Agent": "Day3LearningScraper/1.0 (educational project)"
}


def fetch_page(url):
    """Download one HTML page and return its parsed soup."""
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15,
    )
    response.raise_for_status()

    return BeautifulSoup(response.content, "html.parser")


def extract_books(soup, page_url):
    """Extract book information from a catalogue page."""
    books = []

    for book in soup.select("article.product_pod"):
        title_element = book.select_one("h3 a")
        price_element = book.select_one(".price_color")
        stock_element = book.select_one(".availability")
        rating_element = book.select_one("p.star-rating")

        if not title_element:
            continue

        title = title_element.get("title", "").strip()
        product_url = urljoin(
            page_url,
            title_element.get("href", ""),
        )

        books.append({
            "title": title,
            "price": (
                price_element.get_text(strip=True)
                if price_element else ""
            ),
            "availability": (
                stock_element.get_text(" ", strip=True)
                if stock_element else ""
            ),
            "rating": (
                rating_element.get("class", ["", ""])[1]
                if rating_element
                and len(rating_element.get("class", [])) > 1
                else ""
            ),
            "product_url": product_url,
            "source_url": page_url,
        })

    return books


def scrape_books(max_pages=5):
    """Follow the Next link and collect books from multiple pages."""
    current_url = BASE_URL
    all_books = []
    visited_urls = set()

    for page_number in range(1, max_pages + 1):
        if current_url in visited_urls:
            break

        visited_urls.add(current_url)
        print(f"Scraping page {page_number}: {current_url}")

        try:
            soup = fetch_page(current_url)
        except requests.RequestException as error:
            print(f"Request failed: {error}")
            break

        page_books = extract_books(soup, current_url)
        all_books.extend(page_books)

        next_link = soup.select_one("li.next a")

        if not next_link:
            break

        current_url = urljoin(
            current_url,
            next_link.get("href", ""),
        )

        # Be polite: pause between page requests.
        time.sleep(1)

    return all_books


def save_raw_data(books):
    """Save extracted records to CSV."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "title",
        "price",
        "availability",
        "rating",
        "product_url",
        "source_url",
    ]

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)

    print(f"Saved {len(books)} records to {OUTPUT_FILE}")


if __name__ == "__main__":
    records = scrape_books(max_pages=5)
    save_raw_data(records)
    print(f"Total scraped records: {len(records)}")
