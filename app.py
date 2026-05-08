import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

st.set_page_config(page_title="ML Dashboard", layout="wide")

st.title("Descriptive & Predictive Analysis Dashboard")

# Load trained model
model = joblib.load("business_model.pkl")

# Upload CSV
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:

    # Read dataset
    df = pd.read_csv(uploaded_file)

    # Show dataset
    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Descriptive Analysis
    st.subheader("Descriptive Analysis")

    st.write("Dataset Shape")
    st.write(df.shape)

    st.write("Summary Statistics")
    st.write(df.describe())

    # Missing values
    st.write("Missing Values")
    st.write(df.isnull().sum())

    # Select numeric column
    numeric_columns = df.select_dtypes(include=np.number).columns.tolist()

    if len(numeric_columns) > 0:

        selected_column = st.selectbox(
            "Select Column for Visualization",
            numeric_columns
        )

        # Histogram
        fig, ax = plt.subplots()
        ax.hist(df[selected_column], bins=20)

        ax.set_title(f"Distribution of {selected_column}")
        ax.set_xlabel(selected_column)
        ax.set_ylabel("Frequency")

        st.pyplot(fig)

    # Predictive Analysis
st.subheader("Predictive Analysis")

st.write("Enter values for prediction")

quantity = st.number_input("Enter Quantity")
unit_price = st.number_input("Enter Unit Price")
discount = st.number_input("Enter Discount Percent")

input_data = [[quantity, unit_price, discount]]

if st.button("Predict"):

    prediction = model.predict(input_data)

    st.success(f"Predicted Sales: {prediction[0]}")
