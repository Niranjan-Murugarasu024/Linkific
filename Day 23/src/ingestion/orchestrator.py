from datetime import datetime, timezone
from pathlib import Path
import json, uuid
from sqlalchemy import text
from src.ingestion.staging_loader import save_raw, load_records
from src.monitoring.logger import get_logger
log = get_logger(__name__)

def run_pipeline(sources, engine):
    run_id = "run_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]
    started = datetime.now(timezone.utc).isoformat()
    summary, failures = {}, []
    log.info("Pipeline started run_id=%s", run_id)
    for name, collector in sources.items():
        try:
            log.info("Extracting source=%s", name)
            records = collector()
            if records is None: records = []
            if not isinstance(records, list): records = [records]
            raw_path = save_raw(name, records, run_id)
            load_records(engine, name, records, run_id)
            summary[name] = {"status":"success","records":len(records),"raw_path":raw_path}
            log.info("Completed source=%s records=%d", name, len(records))
        except Exception as exc:
            failures.append(name)
            summary[name] = {"status":"failed","error":str(exc)}
            Path("data/quarantine").mkdir(parents=True, exist_ok=True)
            (Path("data/quarantine") / f"{run_id}_{name}.json").write_text(json.dumps({"run_id":run_id,"source":name,"error":str(exc)}), encoding="utf-8")
            log.exception("Source failed; continuing: %s", name)
    status = "partial_success" if failures and len(failures)<len(sources) else ("failed" if failures else "success")
    with engine.begin() as c:
        c.execute(text("INSERT OR REPLACE INTO ingestion_runs VALUES (:r,:s,:e,:st,:summary)"),
                  {"r":run_id,"s":started,"e":datetime.now(timezone.utc).isoformat(),"st":status,"summary":json.dumps(summary)})
    log.info("Pipeline finished run_id=%s status=%s", run_id, status)
    return {"run_id":run_id,"status":status,"summary":summary}
