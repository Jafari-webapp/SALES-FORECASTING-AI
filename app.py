# ==============================
# IMPORTS
# ==============================
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# ==============================
# PAGE CONFIG
# ==============================
st.title("MACHINE LEARNING DASHBOARD")
st.set_page_config(page_title="ML Dashboard", layout="wide")

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #00ffd5;
}
.stButton>button {
    background-color: #00ffd5;
    color: black;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# DATABASE
# ==============================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
''')

# default user (fix duplicate insert)
c.execute("SELECT COUNT(*) FROM users")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO users VALUES('admin','admin')")
    conn.commit()

# ==============================
# SESSION INIT
# ==============================
if "login" not in st.session_state:
    st.session_state["login"] = False

# ==============================
# LOGIN FUNCTION
# ==============================
def login():
    st.sidebar.title("🔐 Login Panel")

    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        result = c.fetchone()

        if result:
            st.session_state["login"] = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# ==============================
# LOGIN CHECK
# ==============================
if not st.session_state["login"]:
    login()
    st.stop()

# ==============================
# TITLE
# ==============================
st.title("📊 ML Descriptive & Predictive Analysis Dashboard")

# ==============================
# FILE UPLOAD
# ==============================
file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if file:

    df = pd.read_csv(file)

    st.subheader("📌 Dataset Preview")
    st.dataframe(df.head())

    # ==============================
    # KPI METRICS
    # ==============================
    st.subheader("📈 KPI Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())
    col4.metric("Duplicate Rows", df.duplicated().sum())

    # ==============================
    # DESCRIPTIVE ANALYSIS
    # ==============================
    st.subheader("📊 Descriptive Analysis")
    st.dataframe(df.describe())

    # ==============================
    # VISUALIZATION
    # ==============================
    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        selected_col = st.selectbox("Select Column for Visualization", numeric_cols)

        st.subheader("📊 Bar Chart")
        st.plotly_chart(px.bar(df, y=selected_col), use_container_width=True)

        st.subheader("📈 Line Chart")
        st.plotly_chart(px.line(df, y=selected_col), use_container_width=True)

        st.subheader("🥧 Pie Chart")

        if df[selected_col].nunique() > 10:
            pie_data = df[selected_col].round().value_counts().head(10)
        else:
            pie_data = df[selected_col].value_counts()

        st.plotly_chart(
            px.pie(values=pie_data.values, names=pie_data.index),
            use_container_width=True
        )

    # ==============================
    # PREDICTIVE ANALYSIS
    # ==============================
    st.subheader("🤖 Predictive Analysis (Linear Regression)")

    if len(numeric_cols) >= 2:

        target = st.selectbox("Select Target Column", numeric_cols)

        features = st.multiselect(
            "Select Feature Columns",
            [col for col in numeric_cols if col != target]
        )

        if len(features) > 0:

            # CLEAN DATA (IMPORTANT FIX)
            df_model = df[features + [target]].dropna()

            X = df_model[features]
            y = df_model[target]

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            model = LinearRegression()
            model.fit(X_train, y_train)

            predictions = model.predict(X_test)

            st.write("📉 Model Performance")
            st.write("R2 Score:", r2_score(y_test, predictions))
            st.write("MSE:", mean_squared_error(y_test, predictions))

            # ==============================
            # ACTUAL VS PREDICTED
            # ==============================
            st.subheader("📊 Actual vs Predicted")

            fig = px.scatter(
                x=y_test,
                y=predictions,
                labels={"x": "Actual", "y": "Predicted"}
            )
            st.plotly_chart(fig, use_container_width=True)

            # ==============================
            # USER INPUT PREDICTION
            # ==============================
            st.subheader("🔮 Make Prediction")

            input_data = []

            for f in features:
                val = st.number_input(f"Enter {f}", value=0.0)
                input_data.append(val)

            if st.button("Predict"):

                input_array = np.array(input_data).reshape(1, -1)
                result = model.predict(input_array)

                st.success(f"Predicted Value: {result[0]}")

else:
    st.info("Upload CSV file to start analysis")

