
# =========================
# IMPORTS
# =========================
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import hashlib
import plotly.express as px
from sklearn.linear_model import LinearRegression
import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="POS System", layout="wide", page_icon="🛒")

# =========================
# =========================

# ======================
# DATABASE SETUP
# ======================
conn = sqlite3.connect("app.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

# ======================
# PASSWORD HASH
# ======================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ======================
# REGISTER USER
# ======================
def register_user(username, password):
    try:
        cursor.execute(
            "INSERT INTO users(username, password) VALUES(?,?)",
            (username, hash_password(password))
        )
        conn.commit()
        return "Account created successfully"
    except:
        return "Username already exists"

# ======================
# LOGIN USER
# ======================
def login_user(username, password):
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    return cursor.fetchone()

# ======================
# RESET PASSWORD
# ======================
def reset_password(username, new_password):
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user:
        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (hash_password(new_password), username)
        )
        conn.commit()
        return "Password changed successfully"
    else:
        return "Username not found"

# ======================
# UI
# ======================
st.title("🔐 Login System")

menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Forgot Password"])

# ======================
# REGISTER
# ======================
if menu == "Register":
    st.subheader("Create Account")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Register"):
        msg = register_user(user, pwd)
        st.success(msg)

# ======================
# LOGIN
# ======================
elif menu == "Login":
    st.subheader("Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_user(user, pwd)
        if result:
            st.success("Login successful 🎉")
        else:
            st.error("Invalid username or password")

# ======================
# FORGOT PASSWORD
# ======================
elif menu == "Forgot Password":
    st.subheader("Reset Password")

    user = st.text_input("Enter Username")
    new_pwd = st.text_input("New Password", type="password")

    if st.button("Reset"):
        msg = reset_password(user, new_pwd)
        st.info(msg)


# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Products",
    "Quantity",
    "Price",
    "Total Sales",
    "Date",
    "Stock",
    "MACHINE LEARNING Prediction",
    ])
 

if st.button("Daily Report"):
    file = make_pdf("Daily Sales Report", daily_data)
    st.success("Report created!")

    with open(file, "rb") as f:
        st.download_button("Download Daily Report", f, file_name=file)

if st.button("Weekly Report"):
    file = make_pdf("Weekly Sales Report", weekly_data)
    st.download_button("Download Weekly Report", open(file, "rb"), file_name=file)

if st.button("Monthly Report"):
    file = make_pdf("Monthly Sales Report", monthly_data)
    st.download_button("Download Monthly Report", open(file, "rb"), file_name=file)        

# =========================


    
# =========================
# END
# =========================

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    products = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    sales = cursor.execute("SELECT SUM(total) FROM sales").fetchone()[0] or 0
    stock = cursor.execute("SELECT SUM(stock) FROM products").fetchone()[0] or 0

    col1.metric("Products", products)
    col2.metric("Sales", sales)
    col3.metric("Stock", stock)

    df = pd.read_sql("SELECT date,total FROM sales", conn)

    if not df.empty:
        st.subheader("📈 Sales Chart")
        fig = px.line(df, x="date", y="total", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🥧 Sales Distribution")
        fig2 = px.pie(df, values="total", names="date", hole=0.5)
        st.plotly_chart(fig2, use_container_width=True)

# =========================
# PRODUCTS CRUD
# =========================
elif menu == "Products":

    st.title("📦 Products CRUD")

    action = st.selectbox("Action", ["Add", "View", "Update", "Delete"])

    if action == "Add":
        name = st.text_input("Name")
        price = st.number_input("Price")
        stock = st.number_input("Stock")

        if st.button("Save"):
            cursor.execute("INSERT INTO products(name,price,stock) VALUES(?,?,?)",
                           (name, price, stock))
            conn.commit()
            st.success("Added")

    if action == "View":
        st.dataframe(pd.read_sql("SELECT * FROM products", conn))

    if action == "Update":
        pid = st.number_input("Product ID")
        price = st.number_input("New Price")

        if st.button("Update"):
            cursor.execute("UPDATE products SET price=? WHERE id=?",
                           (price, pid))
            conn.commit()
            st.success("Updated")

    if action == "Delete":
        pid = st.number_input("Product ID")

        if st.button("Delete"):
            cursor.execute("DELETE FROM products WHERE id=?",
                           (pid,))
            conn.commit()
            st.success("Deleted")

# =========================
# SALES
# =========================
elif menu == "Sales":

    st.title("💰 Sales System")

    products = pd.read_sql("SELECT * FROM products", conn)

    if not products.empty:

        product = st.selectbox("Product", products["name"])
        qty = st.number_input("Qty", min_value=1)

        price = products[products["name"] == product]["price"].values[0]
        total = price * qty

        st.write("Total:", total)

        if st.button("Sell"):
            date = str(datetime.date.today())

            cursor.execute("INSERT INTO sales(product,qty,total,date) VALUES(?,?,?,?)",
                           (product, qty, total, date))
            conn.commit()
            st.success("Sale Recorded")

# =========================
# ML PREDICTION
# =========================
elif menu == "ML Prediction":

    st.title("🤖 Sales Prediction")

    df = pd.read_sql("SELECT * FROM sales", conn)

    if len(df) > 3:

        df["x"] = np.arange(len(df))

        X = df[["x"]]
        y = df["total"]

        model = LinearRegression()
        model.fit(X, y)

        pred = model.predict([[len(df)+1]])[0]

        st.success(f"Next Sales Prediction: {pred:,.0f}")

    else:
        st.warning("Not enough data")



# =========================


    
# =========================
# END
# =========================
