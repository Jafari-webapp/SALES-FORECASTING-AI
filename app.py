import streamlit as st
import mysql.connector
import pandas as pd
import hashlib
import numpy as np
from sklearn.linear_model import LinearRegression
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt

# ================= DATABASE =================
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="shop_db"
    )

conn = get_conn()
cur = conn.cursor()

# ================= PASSWORD HASH =================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Streamlit POS", layout="wide")

# ================= SESSION =================
if "user" not in st.session_state:
    st.session_state.user = None

# ================= LOGIN =================
def login():
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                    (u, hash_pw(p)))
        user = cur.fetchone()

        if user:
            st.session_state.user = user
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Wrong credentials")

# ================= REGISTER =================
def register():
    st.title("🆕 Register")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "cashier"])

    if st.button("Create"):
        cur.execute("INSERT INTO users(username,password,role) VALUES(%s,%s,%s)",
                    (u, hash_pw(p), role))
        conn.commit()
        st.success("Account created")

# ================= RECEIPT =================
def receipt(product, qty, total):
    st.success("🧾 Receipt Generated")
    st.write(f"Product: {product}")
    st.write(f"Qty: {qty}")
    st.write(f"Total: {total}")
    st.write("Thank you!")

# ================= PDF REPORT =================
def generate_pdf():
    cur.execute("SELECT SUM(total) FROM sales")
    total_sales = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM products")
    products = cur.fetchone()[0]

    cur.execute("SELECT product, SUM(qty) FROM sales GROUP BY product")
    top = cur.fetchall()

    cur.execute("SELECT date, SUM(total) FROM sales GROUP BY date")
    data = cur.fetchall()

    dates = [str(i[0]) for i in data]
    values = [i[1] for i in data]

    # GRAPH
    plt.figure()
    plt.plot(dates, values, marker="o")
    plt.xticks(rotation=45)
    plt.tight_layout()
    graph = "graph.png"
    plt.savefig(graph)
    plt.close()

    file = "report.pdf"
    c = canvas.Canvas(file)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 800, "BUSINESS REPORT")

    c.setFont("Helvetica", 12)
    c.drawString(50, 770, f"Date: {datetime.now()}")

    c.drawString(50, 740, f"Total Sales: {total_sales}")
    c.drawString(50, 720, f"Products: {products}")

    profit = total_sales * 0.3
    c.drawString(50, 700, f"Profit Estimate: {profit}")

    y = 660
    c.drawString(50, 680, "Top Products:")
    for t in top:
        c.drawString(60, y, f"{t[0]} - {t[1]}")
        y -= 20

    c.drawImage(graph, 50, 300, width=500, height=250)

    c.save()
    return file

# ================= DASHBOARD =================
def dashboard():
    st.title("📊 Dashboard")

    cur.execute("SELECT SUM(total) FROM sales")
    sales = cur.fetchone()[0] or 0

    cur.execute("SELECT COUNT(*) FROM products")
    prod = cur.fetchone()[0]

    c1, c2 = st.columns(2)
    c1.metric("Total Sales", sales)
    c2.metric("Products", prod)

# ================= PRODUCTS =================
def products():
    st.title("📦 Products")

    n = st.text_input("Name")
    p = st.number_input("Price")
    s = st.number_input("Stock")

    if st.button("Add"):
        cur.execute("INSERT INTO products(name,price,stock) VALUES(%s,%s,%s)",
                    (n, p, s))
        conn.commit()
        st.success("Added")

    df = pd.read_sql("SELECT * FROM products", conn)
    st.dataframe(df)

    d = st.number_input("Delete ID")
    if st.button("Delete"):
        cur.execute("DELETE FROM products WHERE id=%s", (d,))
        conn.commit()
        st.warning("Deleted")

# ================= SALES =================
def sales():
    st.title("💰 Sales")

    df = pd.read_sql("SELECT * FROM products", conn)

    if len(df) == 0:
        st.warning("No products")
        return

    product = st.selectbox("Product", df["name"])
    qty = st.number_input("Qty")

    if st.button("Sell"):
        price = df[df["name"] == product]["price"].values[0]
        total = price * qty

        cur.execute("INSERT INTO sales(product,qty,total) VALUES(%s,%s,%s)",
                    (product, qty, total))
        conn.commit()

        receipt(product, qty, total)

# ================= ML FORECAST =================
def ml():
    st.title("📈 Forecast")

    df = pd.read_sql("SELECT * FROM sales", conn)

    if len(df) < 3:
        st.warning("Not enough data")
        return

    X = np.array(range(len(df))).reshape(-1,1)
    y = df["total"]

    model = LinearRegression()
    model.fit(X, y)

    pred = model.predict([[len(df)+1]])

    st.success(f"Next Sales Prediction: {pred[0]:.2f}")

# ================= MAIN =================
if st.session_state.user is None:
    opt = st.radio("Choose", ["Login", "Register"])

    if opt == "Login":
        login()
    else:
        register()

else:
    st.sidebar.write(f"👤 {st.session_state.user[1]}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    menu = st.sidebar.selectbox("Menu",
                                ["Dashboard", "Products", "Sales", "ML Forecast", "Report"])

    if menu == "Dashboard":
        dashboard()

    elif menu == "Products":
        products()

    elif menu == "Sales":
        sales()

    elif menu == "ML Forecast":
        ml()

    elif menu == "Report":
        st.title("📄 Business Report")

        if st.button("Generate PDF"):
            file = generate_pdf()

            with open(file, "rb") as f:
                st.download_button("Download Report", f, file_name="report.pdf")
