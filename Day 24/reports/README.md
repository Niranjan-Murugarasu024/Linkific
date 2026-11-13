# Validation reports

Running `python scripts/run_pipeline.py` creates timestamped `validation_report_*.json` and `.txt` files in this folder. A report is emitted for each ETL run. The latest report's overall status should be `PASS` before treating the warehouse load as complete.
