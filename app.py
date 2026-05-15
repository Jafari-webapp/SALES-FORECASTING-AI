import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Sales Dashboard Analysis",
    page_icon="📊",
    layout="wide",
)

st.title("Sales Dashboard Analysis")
st.markdown(
    "This dashboard shows sales performance, region comparison, and month-over-month trends with color-coded insights."
)

# Sample sales data
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
for month in months:
    for region in regions:
        for product in products:
            sales = int(
                30000
                + 10000 * regions.index(region)
                + 4000 * products.index(product)
                + (months.index(month) * 1500)
                + (regions.index(region) * 400)
            )
            orders = int(70 + 15 * products.index(product) + 3 * months.index(month))
            rows.append(
                {
                    "Month": month,
                    "Region": region,
                    "Product": product,
                    "Sales": sales,
                    "Orders": orders,
                }
            )

df = pd.DataFrame(rows)

# Sidebar filters
st.sidebar.header("Filters")
selected_region = st.sidebar.selectbox("Choose region", ["All"] + regions)
selected_product = st.sidebar.selectbox("Choose product", ["All"] + products)
selected_month = st.sidebar.selectbox("Choose month", ["All"] + months)

filtered = df.copy()
if selected_region != "All":
    filtered = filtered[filtered["Region"] == selected_region]
if selected_product != "All":
    filtered = filtered[filtered["Product"] == selected_product]
if selected_month != "All":
    filtered = filtered[filtered["Month"] == selected_month]

# Key metrics
sales_total = filtered["Sales"].sum()
orders_total = filtered["Orders"].sum()
avg_order_value = sales_total / orders_total if orders_total else 0

latest_month = filtered["Month"].max() if not filtered.empty else None
previous_month = None
if latest_month:
    months_ordered = [m for m in months if m != latest_month]
    previous_month = months_ordered[-1] if months_ordered else None

sales_change = 0
if latest_month and previous_month is not None:
    latest_sum = filtered[filtered["Month"] == latest_month]["Sales"].sum()
    previous_sum = filtered[filtered["Month"] == previous_month]["Sales"].sum()
    if previous_sum:
        sales_change = (latest_sum - previous_sum) / previous_sum * 100

color_code = "green" if sales_change >= 5 else "orange" if sales_change >= 0 else "red"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${sales_total:,.0f}")
col2.metric("Total Orders", f"{orders_total:,}")
col3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
col4.metric(
    "Sales Change",
    f"{sales_change:+.1f}%",
    delta_color="normal",
)

st.markdown(
    f"**Color code**: <span style='color:green'>Green = strong growth</span>, <span style='color:orange'>Orange = flat/moderate</span>, <span style='color:red'>Red = decline</span>.",
    unsafe_allow_html=True,
)

# Sales by month chart
monthly = (
    filtered.groupby("Month", sort=False)["Sales"]
    .sum()
    .reset_index()
)

sales_line = (
    alt.Chart(monthly)
    .mark_line(point=True)
    .encode(
        x=alt.X("Month", sort=months, title="Month"),
        y=alt.Y("Sales", title="Sales ($)"),
        tooltip=["Month", alt.Tooltip("Sales", format="$,.")],
    )
    .properties(title="Sales Trend by Month", width=750, height=360)
)

# Sales by region chart
region_summary = (
    filtered.groupby("Region")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)

region_bar = (
    alt.Chart(region_summary)
    .mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5)
    .encode(
        x=alt.X("Region", sort="-y", title="Region"),
        y=alt.Y("Sales", title="Sales ($)"),
        color=alt.Color(
            "Sales",
            scale=alt.Scale(scheme="tealblues"),
            legend=None,
        ),
        tooltip=["Region", alt.Tooltip("Sales", format="$,.")],
    )
    .properties(title="Sales by Region", width=500, height=360)
)

# Layout charts
left, right = st.columns([2, 1])
left.altair_chart(sales_line, use_container_width=True)
right.altair_chart(region_bar, use_container_width=True)

# Color-coded table
if not region_summary.empty:
    styled = region_summary.style.background_gradient(
        cmap="RdYlGn",
        subset=["Sales"],
        low=0,
        high=1,
    )
    st.markdown("### Region Sales Summary")
    st.dataframe(styled, height=240)

st.markdown("---")
st.markdown(
    "### Dashboard insights"
    "\n- Green color shows strong sales performance."
    "\n- Orange indicates stable or moderate performance."
    "\n- Red highlights region or month declines that need attention."
)
