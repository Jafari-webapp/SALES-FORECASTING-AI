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
# DATABASE
# =========================
conn = sqlite3.connect("pos.db", check_same_thread=False)
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# PRODUCTS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    stock INTEGER
)
""")

# SALES TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    qty INTEGER,
    total REAL,
    date TEXT
)
""")

conn.commit()

# =========================
# PASSWORD HASH
# =========================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# default admin
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users(username,password) VALUES(?,?)",
                   ("admin", hash_pw("1234")))
    conn.commit()

# =========================
# AUTH FUNCTIONS
# =========================
def login_user(u, p):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (u, hash_pw(p)))
    return cursor.fetchone()

def register_user(u, p):
    try:
        cursor.execute("INSERT INTO users(username,password) VALUES(?,?)",
                       (u, hash_pw(p)))
        conn.commit()
        return True
    except:
        return False

# =========================
# SESSION
# =========================
if "auth" not in st.session_state:
    st.session_state.auth = False

# =========================
# LOGIN + REGISTER PAGE
# =========================
if not st.session_state.auth:

    st.title("🔐 PREFIX SALES SYSTEM")

    mode = st.radio("Select", ["Login", "Register"])

    if mode == "Login":
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.auth = True
                st.success("Login Success")
                st.rerun()
            else:
                st.error("Wrong Credentials")

    if mode == "Register":
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")

        if st.button("Register"):
            if register_user(nu, np):
                st.success("Account Created! Login now")
            else:
                st.error("Username already exists")

    st.stop()

# =========================
# SIDEBAR
# =========================
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Products"
    "Quantity"
    "Price"
    "Total Sales",
    "Date"
    "ML Prediction",
  
])

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
