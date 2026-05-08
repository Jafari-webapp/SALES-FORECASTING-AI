
import streamlit as st
import pandas as pd
# Boxplot
    st.subheader("📦 Boxplot")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x=df[column], ax=ax2)
    st.pyplot(fig2)

    # Correlation heatmap
    st.subheader("🔥 Correlation Heatmap")
    fig3, ax3 = plt.subplots()
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax3)
    st.pyplot(fig3)

else:
    st.info("Upload a CSV file to start analysis")
    df = pd.read_csv(uploaded_file)

    # =========================
    # DESCRIPTIVE ANALYSIS
    # =========================
    st.header("📌 Descriptive Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

    with col2:
        st.subheader("Statistics Summary")
        st.write(df.describe())

    st.subheader("Missing Values")
    st.write(df.isnull().sum())
    df = pd.read_csv(uploaded_file)

    # =========================
    # DESCRIPTIVE ANALYSIS
    # =========================
    st.header("📌 Descriptive Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Dataset Preview")
        st.dataframe(df.head())

    with col2:
        st.subheader("Statistics Summary")
        st.write(df.describe())

    st.subheader("Missing Values")
    st.write(df.isnull().sum())
   # Correlation heatmap
    st.subheader("🔥 Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # =========================
    # VISUAL ANALYSIS
    # =========================
    st.header("📊 Data Visualization")

    column = st.selectbox("Select Column for Distribution", df.columns)

    fig2, ax2 = plt.subplots()
    sns.histplot(df[column], kde=True, ax=ax2)
    st.pyplot(fig2)

    # =========================
    # PREDICTIVE ANALYSIS
    # =========================
    st.header("🤖 Predictive Analysis (ML Model)")

  # Select features
    target = st.selectbox("Select Target Column (y)", df.columns)

    features = st.multiselect("Select Feature Columns (X)", df.columns)

    if len(features) > 0:

        X = df[features]
        y = df[target]

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)
    # Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        st.subheader("📈 Model Performance")
        st.write("R² Score:", r2)
        st.write("RMSE:", rmse)

        # Prediction vs Actual plot
        fig3, ax3 = plt.subplots()
        ax3.scatter(y_test, y_pred)
        ax3.set_xlabel("Actual")
        ax3.set_ylabel("Predicted")
        ax3.set_title("Actual vs Predicted")
        st.pyplot(fig3)

        # =========================
        # SINGLE PREDICTION UI
        # =========================
        st.subheader("🔮 Make Prediction")

        input_data = []


        for col in features:
            val = st.number_input(f"Enter {col}", value=0.0)
            input_data.append(val)

        if st.button("Predict"):
            prediction = model.predict([input_data])
            st.success(f"Predicted {target}: {prediction[0]}")

else:
    st.info("Upload CSV file to start analysis")
