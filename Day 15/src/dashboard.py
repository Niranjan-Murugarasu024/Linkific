"""Interactive Streamlit dashboard for the synthetic sales dataset.

Run from the project root:
    streamlit run src/dashboard.py
Install dependencies first with: pip install -r requirements.txt
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sales.csv"

st.set_page_config(page_title="Sales Visualization Dashboard", page_icon="📊", layout="wide")
st.title("📊 Sales Performance Dashboard")
st.caption("Fictional retail data for visualization practice. This is not real business performance data.")

@st.cache_data
def load_data():
    data = pd.read_csv(DATA, parse_dates=["order_date"])
    data["month"] = data["order_date"].dt.to_period("M").dt.to_timestamp()
    return data

if not DATA.exists():
    st.error("Dataset missing. From the project root, run: python src/generate_data.py")
    st.stop()

df = load_data()
with st.sidebar:
    st.header("Filters")
    min_date, max_date = df["order_date"].min().date(), df["order_date"].max().date()
    date_range = st.date_input("Order date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    regions = st.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
    categories = st.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
    channels = st.multiselect("Sales channel", sorted(df["channel"].unique()), default=sorted(df["channel"].unique()))

filtered = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    filtered = filtered[filtered["order_date"].between(start_date, end_date + pd.Timedelta(days=1) - pd.Timedelta(seconds=1))]
filtered = filtered[filtered["region"].isin(regions) & filtered["category"].isin(categories) & filtered["channel"].isin(channels)]

if filtered.empty:
    st.warning("No records match these filters. Select more categories, channels, or regions.")
    st.stop()

sales_total = filtered["sales"].sum()
profit_total = filtered["profit"].sum()
orders = filtered["order_id"].nunique()
margin = (profit_total / sales_total * 100) if sales_total else 0
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"₹{sales_total:,.0f}")
k2.metric("Total Profit", f"₹{profit_total:,.0f}")
k3.metric("Orders", f"{orders:,}")
k4.metric("Profit Margin", f"{margin:.1f}%")

monthly = filtered.groupby("month", as_index=False).agg(sales=("sales", "sum"), profit=("profit", "sum"), orders=("order_id", "nunique"))
left, right = st.columns(2)
with left:
    st.subheader("Sales over time")
    fig = px.line(monthly, x="month", y="sales", markers=True, title="Monthly Sales", template="plotly_white", labels={"month": "Month", "sales": "Sales (₹)"})
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Sales by category")
    by_category = filtered.groupby("category", as_index=False).agg(sales=("sales", "sum"), profit=("profit", "sum"))
    fig = px.bar(by_category.sort_values("sales", ascending=False), x="category", y="sales", color="category", title="Category Sales", template="plotly_white", labels={"category": "Category", "sales": "Sales (₹)"})
    st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Sales vs. profit")
    fig = px.scatter(filtered, x="sales", y="profit", color="category", size="quantity", hover_data=["order_id", "region", "channel", "discount"], template="plotly_white", labels={"sales": "Sales (₹)", "profit": "Profit (₹)"})
    fig.add_hline(y=0, line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Sales by region and channel")
    pivot = filtered.pivot_table(index="region", columns="channel", values="sales", aggfunc="sum", fill_value=0)
    fig = px.imshow(pivot, text_auto=".2s", aspect="auto", title="Sales Heatmap", labels={"x": "Channel", "y": "Region", "color": "Sales (₹)"}, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Filtered records")
st.dataframe(filtered.sort_values("order_date", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered data as CSV", data=filtered.to_csv(index=False).encode("utf-8"), file_name="filtered_sales.csv", mime="text/csv")
