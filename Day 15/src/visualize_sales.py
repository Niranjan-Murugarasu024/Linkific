"""Generate 30+ static and interactive charts from data/sales.csv.

Run from the project root:
    python src/visualize_sales.py

PNG files are written for Matplotlib/Seaborn plots; HTML files are written for Plotly.
All charts use a consistent theme, readable labels, units, and figure sizes.
"""
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Allows PNG export on machines without a desktop display.
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sales.csv"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.figsize": (10, 6), "axes.titlesize": 14, "axes.labelsize": 11})

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run `python src/generate_data.py` first.")

df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
df["weekday"] = df["order_date"].dt.day_name()
df["order_value"] = df["sales"]

# Small helpers keep the exported images consistent and avoid overwriting charts.
def save_mpl(name: str):
    """Save the current Matplotlib figure and close it to free memory."""
    path = OUT / name
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved {path.name}")
    return path


def save_plotly(fig, name: str):
    """Export a self-contained interactive HTML file (no separate image renderer needed)."""
    path = OUT / name
    fig.write_html(path, include_plotlyjs="directory", full_html=True)
    print(f"Saved {path.name}")
    return path


created = []

# ---------------------------------------------------------------------------
# MATPLOTLIB: standard chart types and basic customization (10 outputs)
# ---------------------------------------------------------------------------
monthly = df.groupby("month", as_index=False).agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))

# 01. Line plot: useful for showing a time trend.
plt.figure()
plt.plot(monthly["month"], monthly["sales"], marker="o", linewidth=2)
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Sales (₹)")
plt.xticks(rotation=45)
created.append(save_mpl("mpl_01_monthly_sales_line.png"))

# 02. Bar chart: compares aggregate sales across discrete categories.
cat_sales = df.groupby("category")["sales"].sum().sort_values(ascending=False)
plt.figure()
plt.bar(cat_sales.index, cat_sales.values)
plt.title("Total Sales by Product Category")
plt.xlabel("Category")
plt.ylabel("Sales (₹)")
plt.xticks(rotation=25, ha="right")
created.append(save_mpl("mpl_02_sales_by_category_bar.png"))

# 03. Scatter plot: checks the relationship between revenue and profit.
plt.figure()
plt.scatter(df["sales"], df["profit"], alpha=0.45, s=24)
plt.axhline(0, linewidth=1, linestyle="--")
plt.title("Sales vs. Profit")
plt.xlabel("Sales (₹)")
plt.ylabel("Profit (₹)")
created.append(save_mpl("mpl_03_sales_vs_profit_scatter.png"))

# 04. Histogram: inspects the distribution and skew of transaction sales.
plt.figure()
plt.hist(df["sales"], bins=30, edgecolor="white")
plt.title("Distribution of Transaction Sales")
plt.xlabel("Sales per Order (₹)")
plt.ylabel("Number of Orders")
created.append(save_mpl("mpl_04_sales_distribution_histogram.png"))

# 05. Pie chart: use sparingly; label the share and include a legend-like title.
segment_sales = df.groupby("customer_segment")["sales"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 7))
plt.pie(segment_sales.values, labels=segment_sales.index, autopct="%1.1f%%", startangle=90)
plt.title("Share of Sales by Customer Segment")
created.append(save_mpl("mpl_05_sales_by_segment_pie.png"))

# 06. Subplots: puts related KPIs beside each other while preserving separate scales.
fig, axes = plt.subplots(3, 1, figsize=(11, 10), sharex=True)
axes[0].plot(monthly["month"], monthly["sales"], marker="o")
axes[0].set_title("Monthly Sales")
axes[0].set_ylabel("Sales (₹)")
axes[1].plot(monthly["month"], monthly["profit"], marker="s")
axes[1].set_title("Monthly Profit")
axes[1].set_ylabel("Profit (₹)")
axes[2].bar(monthly["month"], monthly["orders"], width=20)
axes[2].set_title("Monthly Order Count")
axes[2].set_ylabel("Orders")
axes[2].set_xlabel("Month")
plt.xticks(rotation=45)
created.append(save_mpl("mpl_06_monthly_sales_profit_subplots.png"))

# 07. Box plot: highlights medians, spread, and possible outliers by region.
plt.figure()
region_order = df.groupby("region")["sales"].median().sort_values(ascending=False).index
plt.boxplot([df.loc[df["region"] == r, "sales"] for r in region_order], tick_labels=region_order, showfliers=False)
plt.title("Transaction Sales Distribution by Region")
plt.xlabel("Region")
plt.ylabel("Sales (₹)")
created.append(save_mpl("mpl_07_sales_by_region_boxplot.png"))

# 08. Area chart: useful for cumulative totals across time.
plt.figure()
plt.fill_between(monthly["month"], monthly["sales"].cumsum(), alpha=0.35)
plt.plot(monthly["month"], monthly["sales"].cumsum(), linewidth=2)
plt.title("Cumulative Sales Over Time")
plt.xlabel("Month")
plt.ylabel("Cumulative Sales (₹)")
plt.xticks(rotation=45)
created.append(save_mpl("mpl_08_cumulative_sales_area.png"))

# 09. Horizontal bar chart: readable when category labels are long.
subcat_profit = df.groupby("product")["profit"].sum().sort_values()
plt.figure(figsize=(10, 7))
plt.barh(subcat_profit.index, subcat_profit.values)
plt.title("Total Profit by Product")
plt.xlabel("Profit (₹)")
plt.ylabel("Product")
created.append(save_mpl("mpl_09_profit_by_product_horizontal.png"))

# 10. Error bars: compares average sales with a 95% confidence interval approximation.
summary = df.groupby("category")["sales"].agg(["mean", "std", "count"]).sort_values("mean", ascending=False)
ci95 = 1.96 * summary["std"] / np.sqrt(summary["count"])
plt.figure()
plt.errorbar(summary.index, summary["mean"], yerr=ci95, fmt="o", capsize=5)
plt.title("Average Order Sales by Category (95% CI Approximation)")
plt.xlabel("Category")
plt.ylabel("Mean Sales (₹)")
plt.xticks(rotation=25, ha="right")
created.append(save_mpl("mpl_10_avg_sales_errorbar.png"))

# ---------------------------------------------------------------------------
# SEABORN: distribution, category, relationship and statistical plots (10)
# ---------------------------------------------------------------------------
# 11. Histogram with KDE curve: combines counts and smoothed density.
plt.figure()
sns.histplot(data=df, x="sales", bins=30, kde=True, color="steelblue")
plt.title("Sales Distribution with Density Curve")
plt.xlabel("Sales (₹)")
plt.ylabel("Count")
created.append(save_mpl("sns_11_sales_hist_kde.png"))

# 12. Count plot: compares the number of records in each category.
plt.figure()
sns.countplot(data=df, x="category", order=df["category"].value_counts().index, color="steelblue")
plt.title("Number of Orders by Category")
plt.xlabel("Category")
plt.ylabel("Order Count")
plt.xticks(rotation=25, ha="right")
created.append(save_mpl("sns_12_orders_by_category_count.png"))

# 13. Box plot: compare profit spread by region; zero-profit reference is explicit.
plt.figure()
sns.boxplot(data=df, x="region", y="profit", showfliers=False, color="steelblue")
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("Profit Distribution by Region")
plt.xlabel("Region")
plt.ylabel("Profit (₹)")
created.append(save_mpl("sns_13_profit_by_region_box.png"))

# 14. Violin plot: shows both distribution shape and central tendency.
plt.figure()
sns.violinplot(data=df, x="category", y="profit", inner="quartile", cut=0, color="steelblue")
plt.title("Profit Distribution by Category")
plt.xlabel("Category")
plt.ylabel("Profit (₹)")
plt.xticks(rotation=25, ha="right")
created.append(save_mpl("sns_14_profit_by_category_violin.png"))

# 15. Heatmap: correlation is association, not proof of causation.
plt.figure(figsize=(9, 7))
numeric = df[["quantity", "unit_price", "discount", "sales", "profit"]]
sns.heatmap(numeric.corr(), annot=True, fmt=".2f", cmap="vlag", center=0, square=True)
plt.title("Correlation Matrix of Numeric Features")
created.append(save_mpl("sns_15_correlation_heatmap.png"))

# 16. Pair plot: sample rows so that the chart remains readable and quick to render.
pair_df = df[["quantity", "discount", "sales", "profit", "category"]].sample(min(350, len(df)), random_state=42)
g = sns.pairplot(pair_df, vars=["quantity", "discount", "sales", "profit"], hue="category", corner=True, plot_kws={"alpha": 0.55, "s": 18})
g.fig.suptitle("Pair Plot of Numeric Sales Variables (Sample)", y=1.02)
pair_path = OUT / "sns_16_pairplot_numeric.png"
g.savefig(pair_path, dpi=140, bbox_inches="tight")
plt.close(g.fig)
created.append(pair_path)
print(f"Saved {pair_path.name}")

# 17. Regression plot: visually summarizes a linear association.
plt.figure()
sns.regplot(data=df.sample(min(800, len(df)), random_state=2), x="sales", y="profit", color="steelblue", scatter_kws={"alpha": 0.35, "s": 20}, line_kws={"color": "black"})
plt.axhline(0, linestyle="--", linewidth=1)
plt.title("Relationship Between Sales and Profit")
plt.xlabel("Sales (₹)")
plt.ylabel("Profit (₹)")
created.append(save_mpl("sns_17_regression_sales_profit.png"))

# 18. Joint plot: a scatter chart with marginal distributions.
g = sns.jointplot(data=df.sample(min(700, len(df)), random_state=3), x="sales", y="profit", kind="reg", color="steelblue", height=7, scatter_kws={"alpha": 0.4, "s": 20})
g.fig.suptitle("Sales vs Profit with Marginal Distributions", y=1.02)
joint_path = OUT / "sns_18_sales_profit_jointplot.png"
g.savefig(joint_path, dpi=140, bbox_inches="tight")
plt.close(g.fig)
created.append(joint_path)
print(f"Saved {joint_path.name}")

# 19. Bar plot: mean sales and confidence intervals by sales channel.
plt.figure()
sns.barplot(data=df, x="channel", y="sales", errorbar=("ci", 95), color="steelblue")
plt.title("Average Order Sales by Channel (95% CI)")
plt.xlabel("Channel")
plt.ylabel("Mean Sales (₹)")
created.append(save_mpl("sns_19_avg_sales_by_channel_bar.png"))

# 20. Scatter plot: discount versus profit, colored by category.
plt.figure()
sns.scatterplot(data=df.sample(min(900, len(df)), random_state=4), x="discount", y="profit", hue="category", alpha=0.65)
plt.title("Discount vs Profit by Category")
plt.xlabel("Discount Rate")
plt.ylabel("Profit (₹)")
created.append(save_mpl("sns_20_discount_profit_scatter.png"))

# ---------------------------------------------------------------------------
# PLOTLY: interactive HTML charts (12 outputs)
# ---------------------------------------------------------------------------
plot_template = "plotly_white"
base = px.line(monthly, x="month", y="sales", markers=True, title="Interactive Monthly Sales Trend", template=plot_template, labels={"month": "Month", "sales": "Sales (₹)"})
base.update_layout(hovermode="x unified")
created.append(save_plotly(base, "plotly_21_monthly_sales_line.html"))

fig = px.scatter(df, x="sales", y="profit", color="category", size="quantity", hover_data=["order_id", "order_date", "region", "discount", "channel"], title="Interactive Sales vs Profit", template=plot_template, labels={"sales": "Sales (₹)", "profit": "Profit (₹)"})
fig.add_hline(y=0, line_dash="dash")
created.append(save_plotly(fig, "plotly_22_interactive_sales_profit_scatter.html"))

sun = df.groupby(["region", "category", "channel"], as_index=False)["sales"].sum()
fig = px.sunburst(sun, path=["region", "category", "channel"], values="sales", title="Sales Breakdown: Region → Category → Channel", template=plot_template)
created.append(save_plotly(fig, "plotly_23_region_category_sunburst.html"))

tree = df.groupby(["category", "product"], as_index=False)["sales"].sum()
fig = px.treemap(tree, path=["category", "product"], values="sales", title="Sales Treemap by Category and Product", template=plot_template)
created.append(save_plotly(fig, "plotly_24_category_product_treemap.html"))

# Sample for performance; the plot remains interactive and rotates in 3D.
three_d = df.sample(min(550, len(df)), random_state=12)
fig = px.scatter_3d(three_d, x="sales", y="profit", z="discount", color="category", hover_data=["order_id", "region"], title="3D View: Sales, Profit and Discount", template=plot_template)
created.append(save_plotly(fig, "plotly_25_3d_sales_profit_discount.html"))

anim = df.copy()
anim["month_label"] = anim["month"].dt.strftime("%Y-%m")
# Aggregate to city/category/month so the animated chart stays performant.
anim_agg = anim.groupby(["month_label", "city", "category"], as_index=False).agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "count"))
fig = px.scatter(anim_agg, x="sales", y="profit", animation_frame="month_label", animation_group="city", size="orders", color="category", hover_name="city", title="Animated City Sales and Profit by Month", range_x=[0, max(10000, anim_agg["sales"].max() * 1.05)], range_y=[min(-1000, anim_agg["profit"].min() * 1.1), max(1000, anim_agg["profit"].max() * 1.1)], template=plot_template)
created.append(save_plotly(fig, "plotly_26_animated_city_performance.html"))

fig = px.histogram(df, x="sales", color="category", nbins=35, marginal="box", title="Interactive Sales Distribution", template=plot_template, labels={"sales": "Sales (₹)"})
created.append(save_plotly(fig, "plotly_27_sales_distribution_histogram.html"))

fig = px.area(monthly, x="month", y="profit", title="Monthly Profit Area Chart", template=plot_template, labels={"month": "Month", "profit": "Profit (₹)"})
fig.add_hline(y=0, line_dash="dash")
created.append(save_plotly(fig, "plotly_28_monthly_profit_area.html"))

region_metrics = df.groupby("region", as_index=False).agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
fig = px.bar(region_metrics, x="region", y="sales", color="region", hover_data=["profit", "orders"], title="Sales by Region", template=plot_template, labels={"sales": "Sales (₹)"})
created.append(save_plotly(fig, "plotly_29_sales_by_region_bar.html"))

fig = px.scatter(df.sample(min(900, len(df)), random_state=9), x="discount", y="profit", size="sales", color="channel", hover_data=["category", "region", "order_id"], title="Discount vs Profit (Bubble Size = Sales)", template=plot_template, labels={"discount": "Discount Rate", "profit": "Profit (₹)", "sales": "Sales (₹)"})
fig.add_hline(y=0, line_dash="dash")
created.append(save_plotly(fig, "plotly_30_discount_profit_bubble.html"))

pivot = df.pivot_table(index="category", columns="channel", values="sales", aggfunc="sum", fill_value=0)
fig = px.imshow(pivot, text_auto=".2s", aspect="auto", color_continuous_scale="Blues", title="Sales Heatmap: Category × Channel", labels={"x": "Channel", "y": "Category", "color": "Sales (₹)"}, template=plot_template)
created.append(save_plotly(fig, "plotly_31_channel_category_heatmap.html"))

parallel = df.sample(min(600, len(df)), random_state=15).copy()
parallel["category_code"] = parallel["category"].astype("category").cat.codes
fig = px.parallel_coordinates(parallel, dimensions=["quantity", "unit_price", "discount", "sales", "profit", "category_code"], color="profit", title="Parallel Coordinates: Order Characteristics", template=plot_template, color_continuous_scale=px.colors.diverging.Tealrose)
created.append(save_plotly(fig, "plotly_32_parallel_coordinates.html"))

# Export a small KPI summary and a manifest for learners to find outputs.
summary_rows = [
    ("records", int(len(df))),
    ("date_start", str(df["order_date"].min().date())),
    ("date_end", str(df["order_date"].max().date())),
    ("total_sales_inr", round(float(df["sales"].sum()), 2)),
    ("total_profit_inr", round(float(df["profit"].sum()), 2)),
    ("average_order_sales_inr", round(float(df["sales"].mean()), 2)),
    ("negative_profit_order_count", int((df["profit"] < 0).sum())),
]
pd.DataFrame(summary_rows, columns=["metric", "value"]).to_csv(OUT / "sales_kpi_summary.csv", index=False)
manifest = {
    "dataset": "data/sales.csv",
    "static_charts_png": sum(p.suffix == ".png" for p in created),
    "interactive_charts_html": sum(p.suffix == ".html" for p in created),
    "files": [p.name for p in created],
    "note": "Synthetic practice dataset. Values are fictional and for learning only."
}
(OUT / "chart_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"\nDone: {len(created)} charts created ({manifest['static_charts_png']} PNG, {manifest['interactive_charts_html']} HTML).")
print(f"Open static charts in: {OUT}")
print("Open any Plotly HTML file in a web browser for hover, zoom, and legend interactions.")
