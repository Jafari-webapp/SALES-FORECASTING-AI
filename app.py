
# ==============================
# IMPORTS
# ==============================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error, r2_score

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="MACHINE LEARNING SALES DASHBOARD", layout="wide")

# ==============================
# CUSTOM CSS (UI DESIGN)
# ==============================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #00ffd5;
}
.stMetric {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 10px;
}
.stButton>button {
    background-color: #00ffd5;
    color: black;
    border-radius: 10px;
    width: 100%;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# TITLE
# ==============================
st.title("📊 AI Sales ML Dashboard (Descriptive + Predictive)")

# ==============================
# UPLOAD FILE
# ==============================
file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if file:

    df = pd.read_csv(file)
    df = df.replace([np.inf, -np.inf], np.nan)

    st.subheader("📌 Dataset Preview")
    st.dataframe(df.head())

    # ==============================
    # KPI SECTION
    # ==============================
    st.subheader("📈 KPI Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing", df.isnull().sum().sum())
    col4.metric("Duplicates", df.duplicated().sum())

    # ==============================
    # REQUIRED COLUMNS
    # ==============================
    required_cols = ["Quantity", "Unit_Price", "Discount_Percent"]

    if all(col in df.columns for col in required_cols):

        # CREATE SALES COLUMN
        df["Sales"] = df["Quantity"] * df["Unit_Price"] * (1 - df["Discount_Percent"]/100)

        st.success("✔ Data ready for analysis")

        # ==============================
        # DESCRIPTIVE ANALYSIS
        # ==============================
        st.subheader("📊 Descriptive Analysis")
        st.dataframe(df.describe())

        # ==============================
        # VISUALIZATION
        # ==============================
        st.subheader("📊 Charts")

        numeric_cols = df.select_dtypes(include=np.number).columns

        selected = st.selectbox("Select Column", numeric_cols)

        st.plotly_chart(px.bar(df, y=selected), use_container_width=True)
        st.plotly_chart(px.line(df, y=selected), use_container_width=True)

        # PIE CHART
        pie_data = df[selected].value_counts().head(10)
        st.plotly_chart(px.pie(values=pie_data.values, names=pie_data.index),
                        use_container_width=True)

        # ==============================
        # PREDICTIVE MODEL
        # ==============================
        st.subheader("🤖 Sales Prediction (Decision Tree)")

        features = st.multiselect(
            "Select Features",
            ["Quantity", "Unit_Price", "Discount_Percent"]
        )

        target = "Sales"

        if len(features) > 0:

            data = df[features + [target]].dropna()

            X = data[features]
            y = data[target]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            model = DecisionTreeRegressor()
            model.fit(X_train, y_train)

            preds = model.predict(X_test)

            st.write("📉 Model Performance")
            st.write("R² Score:", round(r2_score(y_test, preds), 4))
            st.write("MSE:", round(mean_squared_error(y_test, preds), 4))

            st.plotly_chart(
                px.scatter(x=y_test, y=preds,
                           labels={"x": "Actual Sales", "y": "Predicted Sales"}),
                use_container_width=True
            )

            # ==============================
            # LIVE PREDICTION
            # ==============================
            st.subheader("🔮 Predict New Sales")

            q = st.number_input("Quantity", value=1)
            u = st.number_input("Unit Price", value=1.0)
            d = st.number_input("Discount %", value=0.0)

            if st.button("Predict"):

                input_data = np.array([[q, u, d]])
                result = model.predict(input_data)

                st.success(f"Predicted Sales: {round(result[0], 2)}")

    else:
        st.error("❌ CSV lazima iwe na: Quantity, Unit_Price, Discount_Percent")

else:
    st.info("📂 Upload CSV file kuanza dashboard")




