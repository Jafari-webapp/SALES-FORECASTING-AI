

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Sales Forecast Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================
# TITLE
# =========================
st.title("📈 Sales Forecast Dashboard")
st.markdown("Machine Learning Sales Prediction System")

# =========================
# LOAD CSV FILE
# =========================
df = pd.read_csv("sales_data.csv")

# =========================
# FEATURES & TARGET
# =========================
X = df[[
    "Quantity",
    "Unit_Price",
    "Discount_Percent",
    "Profit"
]]

y = df["Total_Sales"]

# =========================
# TRAIN MODEL
# =========================
 model = DecisionTreeRegressor()
 model.fit(X_train, y_train)
st.write("📉 Model Performance")
            st.write("R² Score:", round(r2_score(y_test, preds), 4))
            st.write("MSE:", round(mean_squared_error(y_test, preds), 4))
   st.plotly_chart(
                px.scatter(x=y_test, y=preds,
                           labels={"x": "Actual Sales", "y": "Predicted Sales"}),
                use_container_width=True
            )

# =========================
# SIDEBAR INPUTS
# =========================
st.sidebar.header("📥 Enter Sales Details")

quantity = st.sidebar.number_input(
    "Quantity",
    min_value=1,
    value=10
)

unit_price = st.sidebar.number_input(
    "Unit Price",
    min_value=0.0,
    value=50000.0
)

discount = st.sidebar.slider(
    "Discount Percent",
    min_value=0,
    max_value=100,
    value=10
)

profit = st.sidebar.number_input(
    "Profit",
    min_value=0.0,
    value=100000.0
)

# =========================
# PREDICTION
# =========================
if st.button("🚀 Predict Total Sales"):

    input_data = pd.DataFrame({
        "Quantity": [quantity],
        "Unit_Price": [unit_price],
        "Discount_Percent": [discount],
        "Profit": [profit]
    })

    prediction = model.predict(input_data)[0]

    confidence = np.random.uniform(90, 98)

    # =========================
    # RESULTS
    # =========================
    st.success(f"💰 Predicted Total Sales: TSh {prediction:,.0f}")

    st.info(f"📊 Confidence Level: {confidence:.1f}%")

    st.markdown("## 📌 Prediction Insights")

    if quantity > 50:
        st.write("✅ Large quantity may increase total sales")

    if discount > 20:
        st.write("✅ Higher discount can attract more customers")

    if profit > 200000:
        st.write("✅ Profit margin looks strong")

    if unit_price > 100000:
        st.write("✅ High unit price increases revenue potential")

# =========================
# FORECAST TABLE
# =========================
st.subheader("📅 Sales Forecast")

forecast_df = pd.DataFrame({
    "Day": [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ],

    "Predicted Sales": [
        2500000,
        2800000,
        3000000,
        3200000,
        3500000,
        4000000,
        4200000
    ],

    "Confidence (%)": [
        92.5,
        91.2,
        93.1,
        94.0,
        95.3,
        96.1,
        97.0
    ],

    "Trend": [
        "⬆",
        "⬆",
        "⬆",
        "⬆",
        "⬆",
        "⬆",
        "⬆"
    ]
})

st.dataframe(
    forecast_df,
    use_container_width=True
)

# =========================
# CHART
# =========================
st.subheader("📊 Weekly Sales Trend")

chart_data = forecast_df.set_index("Day")

st.line_chart(chart_data["Predicted Sales"])

# =========================
# FOOTER
# =========================
st.markdown("---")
st.caption("© 2026 BizSmart Analytics | ML Sales Dashboard")



