import sqlite3
from pathlib import Path
import io
from datetime import datetime

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import altair as alt
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import joblib

DATA_DIR = Path(__file__).resolve().parent
DB_PATH = DATA_DIR / "sales.db"
MODEL_PATH = DATA_DIR / "sales_model.joblib"

st.set_page_config(
    page_title="Sales Dashboard Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("Sales Dashboard Analysis")
st.markdown(
    "This dashboard uses Streamlit, SQLite, pandas, NumPy, Matplotlib, Plotly, Altair, scikit-learn, reportlab, and joblib."
)


def initialize_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Month TEXT,
            MonthID INTEGER,
            Region TEXT,
            Product TEXT,
            Sales INTEGER,
            Orders INTEGER
        )
        """
    )
    conn.commit()

    count = cur.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
    if count == 0:
        months = [
            "Jan 2025",
            "Feb 2025",
            "Mar 2025",
            "Apr 2025",
            "May 2025",
            "Jun 2025",
            "Jul 2025",
            "Aug 2025",
            "Sep 2025",
            "Oct 2025",
            "Nov 2025",
            "Dec 2025",
        ]
        regions = ["North", "South", "East", "West"]
        products = ["Widget", "Gadget", "Service"]

        rows = []
        for month_idx, month in enumerate(months, start=1):
            for region_idx, region in enumerate(regions):
                for product_idx, product in enumerate(products):
                    sales = int(
                        25000
                        + 9000 * region_idx
                        + 4500 * product_idx
                        + 1800 * month_idx
                    )
                    orders = int(50 + 10 * product_idx + 4 * month_idx + region_idx * 2)
                    rows.append((month, month_idx, region, product, sales, orders))

        cur.executemany(
            "INSERT INTO sales (Month, MonthID, Region, Product, Sales, Orders) VALUES (?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.commit()
    conn.close()


def load_data(path: Path) -> pd.DataFrame:
    with sqlite3.connect(path) as conn:
        df = pd.read_sql_query("SELECT * FROM sales", conn)
    return df


def build_pdf_report(metrics: dict, region_data: pd.DataFrame, product_data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 50, "Sales Dashboard Report")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, height - 75, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    y = height - 110
    for key, value in metrics.items():
        pdf.drawString(40, y, f"{key}: {value}")
        y -= 18

    y -= 12
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Top Regions")
    pdf.setFont("Helvetica", 12)
    y -= 18
    for _, row in region_data.head(4).iterrows():
        pdf.drawString(40, y, f"{row.Region}: ${row.Sales:,.0f}")
        y -= 16

    y -= 12
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Top Products")
    pdf.setFont("Helvetica", 12)
    y -= 18
    for _, row in product_data.head(4).iterrows():
        pdf.drawString(40, y, f"{row.Product}: ${row.Sales:,.0f}")
        y -= 16

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


initialize_database(DB_PATH)
df = load_data(DB_PATH)

regions = sorted(df["Region"].unique().tolist())
products = sorted(df["Product"].unique().tolist())
months = [
    "Jan 2025",
    "Feb 2025",
    "Mar 2025",
    "Apr 2025",
    "May 2025",
    "Jun 2025",
    "Jul 2025",
    "Aug 2025",
    "Sep 2025",
    "Oct 2025",
    "Nov 2025",
    "Dec 2025",
]

st.sidebar.header("Filters")
selected_region = st.sidebar.selectbox("Region", ["All"] + regions)
selected_product = st.sidebar.selectbox("Product", ["All"] + products)
selected_month = st.sidebar.selectbox("Month", ["All"] + months)

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_product != "All":
    filtered = filtered[filtered["Product"] == selected_product]
if selected_month != "All":
    filtered = filtered[filtered["Month"] == selected_month]

sales_total = int(filtered["Sales"].sum())
orders_total = int(filtered["Orders"].sum())
avg_order_value = float(np.divide(sales_total, orders_total, out=np.array([0.0]), where=orders_total != 0)[0])

monthly_totals = (
    filtered.groupby(["Month", "MonthID"], sort=False)["Sales"]
    .sum()
    .reset_index()
    .sort_values("MonthID")
)
monthly_totals["SalesGrowth"] = monthly_totals["Sales"].pct_change().fillna(0) * 100

sales_change = float(monthly_totals["SalesGrowth"].iloc[-1]) if len(monthly_totals) > 1 else 0.0
color_code = "green" if sales_change >= 5 else "orange" if sales_change >= 0 else "red"

region_summary = (
    filtered.groupby("Region")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)
product_summary = (
    filtered.groupby("Product")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${sales_total:,.0f}")
col2.metric("Total Orders", f"{orders_total:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric("Latest Growth", f"{sales_change:+.1f}%", delta_color="normal")

st.markdown(
    f"**Color code**: <span style='color:green'>Green = strong growth</span>, "
    f"<span style='color:orange'>Orange = stable/moderate</span>, "
    f"<span style='color:red'>Red = decline</span>.",
    unsafe_allow_html=True,
)

st.markdown("---")

# Altair line chart
sales_line = (
    alt.Chart(monthly_totals)
    .mark_line(point=True)
    .encode(
        x=alt.X("Month", sort=months, title="Month"),
        y=alt.Y("Sales", title="Sales ($)"),
        tooltip=["Month", alt.Tooltip("Sales", format="$,.")],
        color=alt.value("#1f77b4"),
    )
    .properties(title="Sales Trend by Month", width=750, height=380)
)

# Plotly regional bar
region_bar = px.bar(
    region_summary,
    x="Region",
    y="Sales",
    color="Sales",
    color_continuous_scale="Tealgrn",
    title="Sales by Region",
    labels={"Sales": "Sales ($)"},
)
region_bar.update_layout(showlegend=False)

# Matplotlib orders distribution
plt.figure(figsize=(6, 4))
bins = np.arange(filtered["Orders"].min() - 2, filtered["Orders"].max() + 4, 3)
plt.hist(filtered["Orders"], bins=bins, color="#2a9d8f", edgecolor="white")
plt.title("Order Distribution")
plt.xlabel("Orders")
plt.ylabel("Frequency")
plt.tight_layout()

left, right = st.columns([2, 1])
left.altair_chart(sales_line, use_container_width=True)
right.plotly_chart(region_bar, use_container_width=True)

st.markdown("### Orders Distribution")
st.pyplot(plt.gcf())

st.markdown("---")

# Train or load regression model
X = df[["MonthID"]].values
y = df["Sales"].values
model = LinearRegression()
model.fit(X, y)
joblib.dump(model, MODEL_PATH)
next_month_id = df["MonthID"].max() + 1
predicted = model.predict(np.array([[next_month_id]]))[0]

st.subheader("Sales Forecast")
st.write(f"Predicted sales for month ID {next_month_id}: ${predicted:,.0f}")

# Clustering by region
region_cluster = region_summary.copy()
if len(region_cluster) >= 3:
    cluster_model = KMeans(n_clusters=3, random_state=42)
    region_cluster["Cluster"] = cluster_model.fit_predict(region_cluster[["Sales"]])
    st.markdown("### Region Clusters")
    st.dataframe(region_cluster, height=220)
else:
    st.markdown("### Region Clusters")
    st.write("Not enough regions to cluster.")

st.markdown("---")

metrics = {
    "Total Sales": f"${sales_total:,.0f}",
    "Total Orders": f"{orders_total:,}",
    "Average Order Value": f"${avg_order_value:,.2f}",
    "Latest Sales Growth": f"{sales_change:+.1f}%",
}

if st.button("Download PDF Summary"):
    pdf_bytes = build_pdf_report(metrics, region_summary, product_summary)
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name="sales_dashboard_report.pdf",
        mime="application/pdf",
    )

st.markdown("### Raw Data Preview")
st.dataframe(filtered.reset_index(drop=True))
