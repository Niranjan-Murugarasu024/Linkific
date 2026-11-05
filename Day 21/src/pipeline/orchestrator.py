from pathlib import Path
import pandas as pd
from src.collectors.api_collector import collect_apis
from src.collectors.database_collector import collect_sqlite, collect_postgres
from src.collectors.file_collector import collect_files
from src.collectors.web_scraper import scrape_example
from src.collectors.ftp_collector import collect_sftp
from src.transformations.schema_mapping import standardize_customer_columns,add_source_metadata
from src.transformations.data_cleaning import clean_customers
from src.transformations.format_converter import convert_examples
from src.integration.data_lineage import write_lineage
from src.warehouse.postgres_loader import load_dataframe
from src.utils.logger import get_logger
log=get_logger("pipeline")

def run_pipeline():
    Path("data/processed").mkdir(parents=True,exist_ok=True)
    log.info("Starting Day 21 collection pipeline")
    api=collect_apis()                 # three REST APIs
    files=collect_files()               # CSV, XLSX, JSON
    sqlite_df=collect_sqlite()          # SQLite source database
    postgres_df=collect_postgres()       # optional PostgreSQL source
    scrape_example()                    # web scraping
    collect_sftp()                      # optional SFTP
    convert_examples()                   # XML, Parquet, Avro examples

    customers=files["customers"]
    customers=standardize_customer_columns(customers)
    customers=clean_customers(customers)
    customers=add_source_metadata(customers,"sample_csv")
    customers.to_csv("data/processed/standardized_customers.csv",index=False)

    sales=files["sales"]
    integrated=sales.merge(customers.drop(columns=["source_system","ingested_at"],errors="ignore"),
                           on="customer_id",how="left")
    integrated.to_csv("data/processed/integrated_sales.csv",index=False)

    # Keep source-level audit information, even when optional sources are unavailable.
    source_names=list(api.keys())+["csv","excel","json","sqlite","postgres_optional","web_scrape","sftp_optional"]
    lineage=write_lineage(source_names,"data/processed/integrated_sales.csv",len(integrated))
    result=load_dataframe(integrated,table="integrated_sales")
    log.info("Pipeline completed: %s",result)
    return {"rows":len(integrated),"warehouse":result,"lineage":lineage}

if __name__=="__main__":
    print(run_pipeline())
