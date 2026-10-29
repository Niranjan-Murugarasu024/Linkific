# Sales Data Visualization Lab

A beginner-friendly data visualization project using **Matplotlib**, **Seaborn**, and **Plotly**. It includes a reproducible synthetic e-commerce dataset, 32 chart outputs, a filterable Streamlit dashboard, and a chart-selection guide.

> **Data note:** `data/sales.csv` is fictional practice data generated with a fixed random seed. It does not contain real people, customers, or company results.

## Project structure

```text
sales_visualization_project/
├── data/
│   └── sales.csv                    # 1,600 fictional order records
├── notebooks/
│   └── visualization_lab.ipynb      # Guided practice notebook
├── outputs/                         # Generated PNG and interactive HTML charts
│   ├── chart_manifest.json
│   ├── plotly.min.js                # Shared JavaScript runtime for HTML charts
│   └── sales_kpi_summary.csv
├── src/
│   ├── generate_data.py             # Rebuild the sample dataset
│   ├── visualize_sales.py           # Generate 32 charts
│   └── dashboard.py                 # Interactive Streamlit dashboard
├── .gitignore
├── requirements.txt
└── README.md
```

## 1. Setup on Windows PowerShell

Open PowerShell and move to the folder where you extracted the project. For example:

```powershell
cd "E:\DataVisualization\sales_visualization_project"
```

Create and activate a virtual environment so the project dependencies do not mix with other Python projects:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If Python 3.11 is not installed, use `py -m venv .venv` instead. If PowerShell blocks activation, run the following in that PowerShell session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Generate or inspect the dataset

The `data/sales.csv` file is included. To regenerate it, run:

```powershell
python src/generate_data.py
```

To inspect the first few records and column types quickly:

```powershell
python -c "import pandas as pd; d=pd.read_csv('data/sales.csv'); print(d.head()); print(d.info()); print(d.describe(include='all'))"
```

### Dataset dictionary

| Column | Meaning | Example |
|---|---|---|
| `order_id` | Unique fictional transaction identifier | `ORD-00001` |
| `order_date` | Transaction date | `2024-03-17` |
| `region` | Broad sales region | `South` |
| `city` | Fictional dataset's city field | `Coimbatore` |
| `category` | Product category | `Electronics` |
| `product` | Product name | `Headphones` |
| `quantity` | Units in the transaction | `2` |
| `unit_price` | Price before discount, in INR | `2400.00` |
| `discount` | Discount fraction from 0 to 0.30 | `0.10` means 10% |
| `sales` | Revenue after discount, in INR | `4320.00` |
| `profit` | Simulated transaction profit, in INR | `900.00` |
| `channel` | Order channel | `Online` |
| `customer_segment` | Broad customer group | `Consumer` |

`profit` is simulated for teaching purposes; do not interpret it as real accounting data.

## 3. Generate all visualizations

From the project root, run:

```powershell
python src/visualize_sales.py
```

The script creates **20 static PNG files and 12 interactive Plotly HTML files** inside `outputs/`, along with `sales_kpi_summary.csv` and `chart_manifest.json`.

Open the `outputs` folder in File Explorer. Double-click any `.png` file to inspect a static chart. Double-click any `.html` file to open an interactive Plotly chart in a browser. Keep `plotly.min.js` in the same `outputs/` folder as the HTML files so the charts load correctly. In an interactive chart, hover over data points, zoom, pan, and click legend entries to hide/show series.

To see which chart files were created, open `outputs/chart_manifest.json`. The KPI summary is in `outputs/sales_kpi_summary.csv`.

## 4. Launch the interactive dashboard

```powershell
streamlit run src/dashboard.py
```

Streamlit prints a local URL (usually `http://localhost:8501`). Open it in your browser. Use the left sidebar to filter by date, region, category, and channel. The KPIs and charts update to reflect the filters. Scroll down to inspect records or download the filtered data as CSV.

To stop the dashboard, focus the PowerShell window and press `Ctrl+C`.

## 5. Run the guided notebook

```powershell
jupyter notebook
```

Open `notebooks/visualization_lab.ipynb` in the browser. Run the cells from top to bottom. If using VS Code, open the notebook and select the `.venv` Python interpreter as the kernel.

## Chart catalogue and when to use each one

| # | Library | Chart | Best used for | Watch out for |
|---:|---|---|---|---|
| 1 | Matplotlib | Line | Trends over time | Keep chronological order; avoid too many lines |
| 2 | Matplotlib | Bar | Comparing categories | Start the bar axis at zero in ordinary comparisons |
| 3 | Matplotlib | Scatter | Relationship between two numeric variables | Overplotting; try transparency or sampling |
| 4 | Matplotlib | Histogram | Distribution of a numeric measure | Bin width changes the visible shape |
| 5 | Matplotlib | Pie | Part-to-whole share for a few groups | Avoid many slices; a bar chart is often easier to compare |
| 6 | Matplotlib | Subplots | Related metrics in a common time window | Label each panel and keep scales clear |
| 7 | Matplotlib | Box plot | Median, spread, and outliers | It hides detailed distribution shape |
| 8 | Matplotlib | Area | Cumulative or total magnitude over time | Filled areas can exaggerate differences |
| 9 | Matplotlib | Horizontal bar | Ranking long labels | Sort values to make ranking easy to scan |
| 10 | Matplotlib | Error bar | Estimate plus uncertainty interval | State what interval/error bar represents |
| 11 | Seaborn | Histogram + KDE | Distribution and smoothed density | KDE can mislead on small or bounded samples |
| 12 | Seaborn | Count plot | Frequency of categories | Count records, not necessarily unique customers |
| 13 | Seaborn | Box plot | Compare distributions across groups | Extreme values may dominate scale |
| 14 | Seaborn | Violin plot | Shape and density by group | Width indicates density, not group size unless encoded |
| 15 | Seaborn | Correlation heatmap | Pairwise linear association | Correlation does not establish causation |
| 16 | Seaborn | Pair plot | Scan several variable pairs | Becomes cluttered with many variables/records |
| 17 | Seaborn | Regression plot | Linear association and fitted trend | A straight line may not fit nonlinear data |
| 18 | Seaborn | Joint plot | Relationship plus marginal distributions | Use sampling for large data |
| 19 | Seaborn | Bar plot with CI | Group mean and uncertainty | Means can hide skew and outliers |
| 20 | Seaborn | Hue scatter plot | Explore group differences | Use a colorblind-friendly palette in production |
| 21 | Plotly | Interactive line | Trend exploration and hover detail | Keep time axis sorted |
| 22 | Plotly | Interactive scatter/bubble | Multi-variable exploration | Bubble area and size scales can be hard to compare |
| 23 | Plotly | Sunburst | Hierarchical part-to-whole data | Keep the hierarchy meaningful and limited |
| 24 | Plotly | Treemap | Nested category contribution | Labels can be crowded in small rectangles |
| 25 | Plotly | 3D scatter | Explore three numeric dimensions | Perspective can hide overlaps; use 2D when sufficient |
| 26 | Plotly | Animated scatter | Change across time periods | Fixed axes help comparisons across frames |
| 27 | Plotly | Histogram with marginal box | Distribution plus a compact summary | Interpret bins and outlier points carefully |
| 28 | Plotly | Area | Time-varying magnitude | Negative values are harder to communicate with filled area |
| 29 | Plotly | Regional bar | Compare totals with hover detail | Sort categories when ranking is the main question |
| 30 | Plotly | Bubble scatter | Add size and color to a relationship plot | Too many encodings can overwhelm the reader |
| 31 | Plotly | Heatmap | Compare two categorical dimensions by value | Use a sequential scale for non-negative totals |
| 32 | Plotly | Parallel coordinates | Explore patterns across multiple numeric dimensions | Normalize/scale thoughtfully; many lines create clutter |

## Visualization best practices

1. **Start with a question.** Decide whether you need to compare categories, show a trend, inspect a distribution, or explore a relationship.
2. **Choose the simplest suitable chart.** A 2D line/bar/scatter chart is usually easier to interpret than 3D.
3. **Label clearly.** Give every chart a descriptive title; label axes and units (₹, orders, percentage); explain non-obvious metrics.
4. **Use color deliberately.** Use a consistent color for the same category across charts. Avoid relying on color alone to convey meaning.
5. **Avoid misleading scales.** Bar charts normally start at zero. If a line chart uses a truncated axis, make that choice conspicuous.
6. **Show context.** State time range, filters, sample size, aggregation level, and the meaning of error bars where relevant.
7. **Treat statistics carefully.** Correlation is not causation; confidence intervals depend on assumptions; averages may be affected by skew/outliers.
8. **Keep it accessible.** Use readable fonts, sufficient contrast, distinguishable colors, and concise labels.
9. **Make dashboards actionable.** Include a small number of useful KPIs, meaningful filters, and definitions for each metric.
10. **Check the data first.** Validate missing values, duplicates, units, date parsing, and aggregations before charting.

## Troubleshooting

- **`ModuleNotFoundError`:** Activate `.venv`, then run `pip install -r requirements.txt` again.
- **No chart files appear:** Ensure PowerShell's current directory is the project root, then rerun `python src/visualize_sales.py` and inspect the console for errors.
- **`_SUCCESS`-style empty file confusion:** This project writes readable `.png`, `.html`, `.csv`, and `.json` files. `_SUCCESS` is not used here.
- **Plotly HTML does not open:** Open it with Chrome/Edge. The HTML uses the local `outputs/plotly.min.js` file, so keep that file beside the HTML charts when moving or sharing them.
- **Streamlit command not found:** Activate `.venv`, then run `python -m pip install streamlit` or install the full requirements file.
- **Notebook kernel cannot import libraries:** Select the project's `.venv` interpreter/kernel in Jupyter or VS Code.

## Suggested practice extensions

- Add a rolling 3-month sales average to the time series.
- Compare gross profit margin across categories: `profit / sales * 100`.
- Add date, segment, and city filters to the dashboard.
- Save one key chart as an image and write a 3-sentence insight with the exact time period and metric.
- Replace synthetic data with a public dataset and update the data dictionary before interpreting any findings.
