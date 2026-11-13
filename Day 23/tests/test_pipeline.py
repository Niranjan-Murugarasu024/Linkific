from sqlalchemy import create_engine, text
from src.ingestion.staging_loader import initialize_staging
from src.ingestion.orchestrator import run_pipeline
def test_pipeline_failure_isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    e=create_engine(f"sqlite:///{tmp_path/'stage.db'}"); initialize_staging(e)
    result=run_pipeline({"ok":lambda:[{"id":1}],"bad":lambda:1/0},e)
    assert result["status"]=="partial_success"
    with e.connect() as c:
        assert c.execute(text("select count(*) from ingestion_records")).scalar_one()==1
