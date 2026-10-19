# Python EDA and Data Profiling Project

A reproducible exploratory data analysis practice project with three synthetic datasets, three notebooks, reusable utility modules, and automated HTML profiling reports.

## Datasets
- `data/raw/ecommerce.csv`: order/product/revenue data with deliberately injected quality issues.
- `data/raw/time_series.csv`: daily sales and sessions with trend, weekly variation, a spike, and a missing value.
- `data/raw/customer_behavior.csv`: customer attributes and conversion outcome with missing and extreme values.

These are **synthetic teaching datasets**, not real customer or business records.

## Setup (Windows PowerShell)
```powershell
Set-Location E:\EDA-Project
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m ipykernel install --user --name eda-project --display-name "Python (EDA Project)"
jupyter lab
```
If PowerShell blocks activation, use:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```
Open the notebooks under `notebooks/` and select the `Python (EDA Project)` kernel. Run each notebook from top to bottom. If the project is located somewhere other than `E:\EDA-Project`, the notebooks attempt to use the current directory first.

## Generate reports
Each notebook creates its HTML profiling report in `reports/`. Profiling can take time and memory; if a dataset becomes large, profile a representative sample or use YData Profiling's minimal mode. If `ydata-profiling` is not installed in the active notebook kernel, the report helper warns and creates a basic HTML summary instead. To generate the full report, select the project virtual-environment kernel and install dependencies with `pip install -r requirements.txt`.

## Project checklist
- [ ] Confirm shape, dtypes, keys, date range and duplicate counts
- [ ] Quantify missingness by column and inspect missingness patterns
- [ ] Validate domain rules (e.g. quantity > 0, price > 0, discount between 0 and 1)
- [ ] Calculate mean, median, variance, standard deviation, percentiles, skewness and kurtosis
- [ ] Plot numerical and categorical distributions
- [ ] Check correlations; do not interpret them as causation
- [ ] Screen IQR/rolling-statistic anomalies and investigate rather than automatically delete
- [ ] Analyze trends, seasonality and customer segments
- [ ] Choose statistical tests appropriate to the question and assumptions
- [ ] Record effect sizes, sample sizes, p-values and limitations
- [ ] Generate and inspect HTML profiling reports
- [ ] Write evidence-based findings and recommended follow-ups
- [ ] Preserve raw data and document any transformations

## Statistical cautions
- A p-value is not the probability that the null hypothesis is true.
- Pearson correlation captures linear association and is sensitive to outliers.
- IQR fences are a screening heuristic, not a universal rule for deleting data.
- Time-series rolling windows can create edge effects and may miss structural changes.
- Statistical significance and business significance are different.
