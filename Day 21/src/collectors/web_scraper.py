from pathlib import Path
from bs4 import BeautifulSoup
import requests
from src.utils.logger import get_logger
log=get_logger("scraper")

def scrape_example():
    # Example.com is intentionally a safe, stable demonstration page.
    url="https://example.com"
    response=requests.get(url,timeout=20)
    response.raise_for_status()
    soup=BeautifulSoup(response.text,"html.parser")
    rows=[{"title":soup.title.get_text(strip=True),"description":(soup.find("p").get_text(" ",strip=True) if soup.find("p") else "")}]
    Path("data/raw").mkdir(parents=True,exist_ok=True)
    import pandas as pd
    pd.DataFrame(rows).to_csv("data/raw/scraped_page.csv",index=False)
    log.info("Scraped %d page record(s)",len(rows))
    return rows
