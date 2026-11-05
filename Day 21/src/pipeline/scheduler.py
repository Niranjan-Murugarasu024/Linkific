from datetime import datetime
import time
from src.pipeline.orchestrator import run_pipeline
from src.utils.logger import get_logger
log=get_logger("scheduler")

def run_interval(minutes=60):
    log.info("Interval scheduler started; interval=%s minutes",minutes)
    while True:
        try: run_pipeline()
        except Exception: log.exception("Scheduled pipeline run failed")
        time.sleep(minutes*60)

if __name__=="__main__":
    run_interval()
