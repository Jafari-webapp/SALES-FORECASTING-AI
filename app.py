# =========================
# 1. IMPORTS
# =========================
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import hashlib
import plotly.express as px
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import datetime

# =========================
# 2. PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Smart POS System",
    layout="wide",
    page_icon="🛒"
)

# =========================
# 3. DATABASE
# =========================
conn = sqlite3.connect("pos.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    stock INTEGER
)
""")

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
# 4. PASSWORD HASH
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
# 5. LOGIN
# =========================
def login(u, p):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                   (u, hash_pw(p)))
    return cursor.fetchone()

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🔐 POS LOGIN")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if login(u, p):
            st.session_state.login = True
            st.success("Login Success")
            st.rerun()
        else:
            st.error("Wrong Credentials")

    st.stop()

# =========================
# 6. SIDEBAR
# =========================
menu = st.sidebar.radio("Menu", [
    "Dashboard",
    "Products CRUD",
    "Sales",
    "ML Prediction",
    "Invoice PDF"
])

# =========================
# 7. DASHBOARD
# =========================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    col1, col2, col3 = st.columns(3)

    cursor.execute("SELECT COUNT(*) FROM products")
    products_count = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM sales")
    total_sales = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(stock) FROM products")
    stock = cursor.fetchone()[0] or 0

    col1.metric("Products", products_count)
    col2.metric("Sales", total_sales)
    col3.metric("Stock", stock)

    # SALES GRAPH
    df = pd.read_sql("SELECT date,total FROM sales", conn)

    if not df.empty:
        fig = px.line(df, x="date", y="total", title="Sales Trend")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.pie(df, values="total", names="date")
        st.plotly_chart(fig2, use_container_width=True)

# =========================
# 8. PRODUCTS CRUD
# =========================
elif menu == "Products CRUD":

    st.title("📦 Products CRUD")

    action = st.selectbox("Action", ["Add", "View", "Update", "Delete"])

    # ADD
    if action == "Add":
        name = st.text_input("Product Name")
        price = st.number_input("Price")
        stock = st.number_input("Stock")

        if st.button("Save"):
            cursor.execute("INSERT INTO products(name,price,stock) VALUES(?,?,?)",
                           (name, price, stock))
            conn.commit()
            st.success("Product Added")

    # VIEW
    if action == "View":
        df = pd.read_sql("SELECT * FROM products", conn)
        st.dataframe(df)

    # UPDATE
    if action == "Update":
        id = st.number_input("Product ID")
        price = st.number_input("New Price")

        if st.button("Update"):
            cursor.execute("UPDATE products SET price=? WHERE id=?",
                           (price, id))
            conn.commit()
            st.success("Updated")

    # DELETE
    if action == "Delete":
        id = st.number_input("Product ID")

        if st.button("Delete"):
            cursor.execute("DELETE FROM products WHERE id=?",
                           (id,))
            conn.commit()
            st.success("Deleted")

# =========================
# 9. SALES SYSTEM
# =========================
elif menu == "Sales":

    st.title("💰 Sales")

    products = pd.read_sql("SELECT * FROM products", conn)

    if not products.empty:

        product = st.selectbox("Select Product", products["name"])
        qty = st.number_input("Quantity", min_value=1)

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
# 10. ML PREDICTION
# =========================
elif menu == "ML Prediction":

    st.title("🤖 Sales Prediction")

    df = pd.read_sql("SELECT date,total FROM sales", conn)

    if len(df) > 2:

        df["day"] = np.arange(len(df))

        X = df[["day"]]
        y = df["total"]

        model = LinearRegression()
        model.fit(X, y)

        future = np.array([[len(df)+1]])
        pred = model.predict(future)[0]

        st.success(f"Predicted Next Sales: {pred:,.0f}")

    else:
        st.warning("Not enough data")

# =========================
# 11. INVOICE PDF
# =========================
elif menu == "Invoice PDF":

    st.title("🧾 Invoice Generator")

    product = st.text_input("Product")
    qty = st.number_input("Qty", min_value=1)
    price = st.number_input("Price")

    if st.button("Generate PDF"):

        total = qty * price

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt="POS INVOICE", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Product: {product}", ln=True)
        pdf.cell(200, 10, txt=f"Qty: {qty}", ln=True)
        pdf.cell(200, 10, txt=f"Total: {total}", ln=True)

        pdf.output("invoice.pdf")

        with open("invoice.pdf", "rb") as f:
            st.download_button("Download Invoice", f, "invoice.pdf")

# =========================
# END
# =========================
