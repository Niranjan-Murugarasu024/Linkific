from pathlib import Path
import json
from datetime import datetime, timezone

def write_lineage(source_names, output_path, record_count):
    Path("data/processed").mkdir(parents=True,exist_ok=True)
    lineage={"pipeline":"day21-multi-source","sources":source_names,
      "output":output_path,"record_count":int(record_count),
      "created_at":datetime.now(timezone.utc).isoformat()}
    Path("data/processed/lineage.json").write_text(json.dumps(lineage,indent=2),encoding="utf-8")
    return lineage
