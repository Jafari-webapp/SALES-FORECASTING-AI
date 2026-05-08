










   






   
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
# PAGE CONFIG (MUST BE FIRST STREAMLIT COMMAND)
# ==============================
st.set_page_config(page_title="ML Dashboard", layout="wide")

# ==============================
# CUSTOM CSS
# ==============================
st.markdown("""
<style>
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
# DATABASE SETUP (SAFE)
# ==============================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT UNIQUE,
    password TEXT
)
""")

# insert default admin only once safely
c.execute("SELECT username FROM users WHERE username=?", ("admin",))
if c.fetchone() is None:
    c.execute("INSERT INTO users VALUES (?,?)", ("admin", "admin"))
    conn.commit()

# ==============================
# SESSION STATE
# ==============================
if "login" not in st.session_state:
    st.session_state.login = False

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
        user = c.fetchone()

        if user:
            st.session_state.login = True
            st.success("Login Successful!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

# ==============================
# LOGIN CHECK
# ==============================
if not st.session_state.login:
    login()
    st.stop()

# ==============================
# MAIN TITLE
# ==============================
st.title("📊 ML Descriptive & Predictive Analysis Dashboard")

# ==============================
# FILE UPLOAD
# ==============================
file = st.file_uploader("📂 Upload CSV File", type=["csv"])

if file:

    df = pd.read_csv(file)

    # clean data (important fix)
    df = df.replace([np.inf, -np.inf], np.nan)

    st.subheader("📌 Dataset Preview")
    st.dataframe(df.head())

    # ==============================
    # KPI SECTION
    # ==============================
    st.subheader("📈 KPI Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    col3.metric("Missing Values", int(df.isnull().sum().sum()))
    col4.metric("Duplicate Rows", int(df.duplicated().sum()))

    # ==============================
    # DESCRIPTIVE ANALYSIS
    # ==============================
    st.subheader("📊 Descriptive Analysis")

    if df.select_dtypes(include=np.number).shape[1] > 0:
        st.dataframe(df.describe())
    else:
        st.warning("No numeric columns for description")

    # ==============================
    # VISUALIZATION
    # ==============================
    numeric_cols = df.select_dtypes(include=np.number).columns

    if len(numeric_cols) > 0:

        selected_col = st.selectbox("📊 Select Column", numeric_cols)

        st.plotly_chart(px.bar(df, y=selected_col), use_container_width=True)
        st.plotly_chart(px.line(df, y=selected_col), use_container_width=True)

        pie_data = df[selected_col].value_counts().head(10)

        st.plotly_chart(
            px.pie(values=pie_data.values, names=pie_data.index),
            use_container_width=True
        )

    # ==============================
    # PREDICTIVE ANALYSIS
    # ==============================
    st.subheader("🤖 Predictive Analysis (Linear Regression)")

    if len(numeric_cols) >= 2:

        target = st.selectbox("🎯 Target Column", numeric_cols)

        features = st.multiselect(
            "📌 Feature Columns",
            [c for c in numeric_cols if c != target]
        )

        if len(features) > 0:

            # clean ML data
            df_model = df[features + [target]].dropna()

            if len(df_model) > 10:

                X = df_model[features]
                y = df_model[target]

                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )

                model = LinearRegression()
                model.fit(X_train, y_train)

                preds = model.predict(X_test)

                st.write("📉 Model Performance")
                st.write("R2 Score:", round(r2_score(y_test, preds), 4))
                st.write("MSE:", round(mean_squared_error(y_test, preds), 4))

                st.plotly_chart(
                    px.scatter(x=y_test, y=preds,
                               labels={"x": "Actual", "y": "Predicted"}),
                    use_container_width=True
                )

                # ==============================
                # LIVE PREDICTION
                # ==============================
                st.subheader("🔮 Make New Prediction")

                inputs = []
                for f in features:
                    inputs.append(st.number_input(f, value=0.0))

                if st.button("Predict"):

                    input_array = np.array(inputs).reshape(1, -1)
                    result = model.predict(input_array)

                    st.success(f"Predicted Value: {float(result[0])}")

            else:
                st.warning("Not enough clean data after removing missing values")

else:
    st.info("📂 Upload a CSV file to start analysis")
________________________________________




