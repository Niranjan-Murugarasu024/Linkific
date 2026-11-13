from pathlib import Path
import json
import pandas as pd
from src.monitoring.logger import get_logger
log = get_logger(__name__)

def read_file(path, chunksize=5000):
    path = Path(path); ext = path.suffix.lower()
    if ext == ".csv":
        for chunk in pd.read_csv(path, chunksize=chunksize):
            yield chunk.to_dict("records")
    elif ext in (".xlsx", ".xls"):
        for sheet in pd.ExcelFile(path).sheet_names:
            df = pd.read_excel(path, sheet_name=sheet)
            log.info("Excel sheet=%s rows=%d", sheet, len(df))
            yield df.to_dict("records")
    elif ext == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict): data = data.get("data", [data])
        if not isinstance(data, list): raise ValueError("JSON root must be a list or data-list object")
        for i in range(0, len(data), chunksize): yield data[i:i+chunksize]
    elif ext == ".parquet":
        df = pd.read_parquet(path)
        for i in range(0, len(df), chunksize): yield df.iloc[i:i+chunksize].to_dict("records")
    else: raise ValueError(f"Unsupported format: {ext}")

def collect_files(directory="data/sample"):
    batches = []
    for path in Path(directory).glob("*"):
        if path.is_file() and path.suffix.lower() in {".csv",".xlsx",".xls",".json",".parquet"}:
            try:
                for batch in read_file(path):
                    batches.append({"source_file": path.name, "records": batch})
            except Exception:
                log.exception("File processing failed: %s", path)
    return batches
