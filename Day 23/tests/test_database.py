from sqlalchemy import create_engine
from src.extractors.database_extractor import initialize_sample_source, extract_table
def test_database_extract(tmp_path):
    e=create_engine(f"sqlite:///{tmp_path/'source.db'}")
    initialize_sample_source(e)
    assert len(extract_table(e,"source_orders"))==3
    assert len(extract_table(e,"source_orders","updated_at","2026-11-11T00:00:00"))==2
