# Advanced Pandas Engineering

A hands-on Data Engineering Intern project for DataFrame joins, time-series analysis, Excel automation, and performance optimization.

## Learning outcomes
- Join relational tables with inner/left/right/outer joins, multi-column keys, `validate`, and `indicator`.
- Stack datasets with `concat`.
- Parse dates, build a `DatetimeIndex`, resample daily data to weekly/monthly/yearly summaries, and calculate rolling and lag features.
- Generate a formatted multi-sheet Excel report with `ExcelWriter` and XlsxWriter.
- Improve memory use with dtype selection and categorical columns.
- Compare vectorized calculations with row-wise `apply`; process large CSVs in chunks.

## Requirements
Python 3.10+ recommended. Tested design targets modern pandas 2.x.

## Setup (Windows PowerShell)
```powershell
Set-Location "E:\Advanced-Pandas-Engineering"
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name advanced-pandas --display-name "Python (Advanced Pandas)"
```
If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Run the scripts
Run from the project root:
```powershell
python src\merge_datasets.py
python src\time_series_analysis.py
python src\excel_report.py
python src\large_csv_processor.py
```
The Excel report requires `merge_datasets.py` first. Outputs are written to `reports/`.

## Run the notebooks
```powershell
jupyter notebook
```
Open each notebook in `notebooks/` and execute cells from top to bottom. If launching Jupyter from another directory, the notebooks include a small root-folder check, but running from the project root is the recommended workflow.

## Data files
- `sales.csv`: transactional sales, including date, customer/product IDs, quantity, and revenue.
- `customers.csv`: customer dimension with region and signup date.
- `products.csv`: product dimension with category and unit cost.
- `daily_sales.csv`: daily date series, including zero-sales dates, for resampling and rolling-window practice.

These are small synthetic practice datasets, not real customer records.

## Key concepts and production notes
### Merge versus concat
Use `merge` to relate rows through key columns. Use `concat` to append compatible tables or align them along an axis. Always inspect key uniqueness and unmatched rows. `validate="many_to_one"` is useful when many transaction rows should map to one dimension row.

### Time-series frequency
Use `resample("D")`, `resample("W")`, `resample("ME")`, and `resample("YE")` with pandas 2.x. Choose aggregations according to the metric: revenue is usually summed, while rates may require weighted averages. Never fill missing dates with zero unless missing means truly no activity.

### Excel automation
`ExcelWriter` writes multiple sheets in one workbook. XlsxWriter handles formatting for newly created workbooks; openpyxl is useful for reading and modifying existing `.xlsx` files. Excel has row-count and file-size limits, so large datasets are better stored in a database or Parquet and Excel should be a reporting layer.

### Performance
Prefer vectorized expressions over `DataFrame.apply(axis=1)` for arithmetic. Downcast numeric columns only after checking ranges and precision. `category` can save memory for repeated low-cardinality strings but may not help high-cardinality fields. Chunking bounds memory; aggregate chunk results carefully. `query` is primarily a readability option and is not guaranteed to be faster than boolean indexing.

### Data quality checklist
- Validate primary and foreign keys.
- Check duplicate IDs and null join keys.
- Compare row counts before/after joins.
- Validate date parsing and time zones.
- Reconcile aggregated totals against source totals.
- Make output generation deterministic and log failures in production.

## Suggested workflow
1. Run `merge_datasets.py` and inspect `reports/enriched_sales.csv`.
2. Run `time_series_analysis.py`; compare monthly totals with the source data.
3. Run `excel_report.py`; open the workbook and check all four sheets.
4. Run `large_csv_processor.py`; compare its totals with a full-file `groupby`.
5. Execute all four notebooks and add your own tests and observations.
