from pathlib import Path
import yaml
from dotenv import load_dotenv
from src.collectors.jsonplaceholder import collect as jsonplaceholder
from src.collectors.dummyjson import collect as dummyjson
from src.collectors.countries import collect as countries
from src.scrapers.product_scraper import scrape_books
from src.processors.file_processor import collect_files
from src.extractors.database_extractor import source_engine, initialize_sample_source, extract_table
from src.ingestion.staging_loader import staging_engine, initialize_staging
from src.ingestion.orchestrator import run_pipeline

def main():
    load_dotenv()
    Path("data/sample").mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load(Path("config/config.yaml").read_text(encoding="utf-8"))
    src = source_engine(); initialize_sample_source(src)
    stage = staging_engine(); initialize_staging(stage)
    apis = cfg["apis"]
    sources = {
        "jsonplaceholder": lambda: jsonplaceholder(apis["jsonplaceholder"]),
        "dummyjson": lambda: dummyjson(apis["dummyjson"]),
        "countries": lambda: countries(apis["countries"]),
        "books_scrape": lambda: scrape_books(cfg["scraping"]["url"], cfg["scraping"]["max_pages"]),
        "file_batches": collect_files,
        "source_database": lambda: extract_table(src, "source_orders"),
    }
    result = run_pipeline(sources, stage)
    print("\nINGESTION SUMMARY")
    print("Run:", result["run_id"], "| Status:", result["status"])
    for name, item in result["summary"].items():
        print(f"{name:20} {item['status']:10} {item.get('records','-')} records")
    print("Raw data: data/raw/ | Staging: data/staging/ | Logs: logs/ingestion.log")
    return result

if __name__ == "__main__": main()
