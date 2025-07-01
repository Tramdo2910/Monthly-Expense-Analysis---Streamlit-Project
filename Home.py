import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- User management (simple demo) ---
USERS = {"user1": "pass123", "user2": "letmein"}  # replace with secure method for production

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state["user"] = username
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password")

def logout():
    if st.button("Log out"):
        st.session_state.pop("user", None)
        st.success("Logged out!")
        st.rerun()

# --- Upload or Input Data ---
def get_month_db(year, month):
    """Return db name like transactions_2024_07.db"""
    return f"transactions_{year}_{str(month).zfill(2)}.db"

def upload_csv_and_store():
    st.subheader("Upload a CSV of Transactions")
    file = st.file_uploader("Choose a CSV file", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.dataframe(df)
        # Ask for month to store
        year = st.number_input("Year", min_value=2000, max_value=2100, value=datetime.today().year)
        month = st.number_input("Month", min_value=1, max_value=12, value=datetime.today().month)
        if st.button("Save to Monthly Database"):
            dbname = get_month_db(year, month)
            with sqlite3.connect(dbname) as conn:
                df.to_sql("transactions", conn, if_exists="append", index=False)
            st.success(f"Data saved to {dbname}")

def manual_entry_and_store():
    st.subheader("Add a Transaction Manually")
    category = st.text_input("Category")
    description = st.text_input("Description")
    amount = st.number_input("Amount", step=0.01)
    typ = st.selectbox("Type", ["Income", "Expense"])
    date = st.date_input("Date", value=datetime.today())
    if st.button("Add Transaction"):
        year, month = date.year, date.month
        dbname = get_month_db(year, month)
        new_entry = pd.DataFrame([{
            "Date": date,
            "Category": category,
            "Description": description,
            "Amount": amount,
            "Income/Expense": typ
        }])
        with sqlite3.connect(dbname) as conn:
            new_entry.to_sql("transactions", conn, if_exists="append", index=False)
        st.success(f"Transaction added to {dbname}")


# --- Main app logic ---
if "user" not in st.session_state:
    login()
    st.stop()

logout()  # Show log out button for logged in user

st.title(f"Welcome, {st.session_state['user']}! 👋")
st.write("Choose how to input your transactions below:")

# menu
menu = st.radio("Select Action", ["Upload CSV", "Manual Entry", "Current database"])

if menu == "Upload CSV":
    st.subheader("Upload your transaction CSV")
    file = st.file_uploader("Choose a CSV file", type=["csv"])
    if file:
        df = pd.read_csv(file)
        st.session_state['df'] = df  # Save to session_state
        st.success("Data uploaded! Now select 'View Analysis' to see insights.")

elif menu == "Manual Entry":
    st.subheader("Manual Transaction Entry")
    # Example manual entry form
    with st.form("manual_entry"):
        date = st.date_input("Date")
        category = st.text_input("Category")
        amount = st.number_input("Amount")
        typ = st.selectbox("Type", ["Income", "Expense"])
        submitted = st.form_submit_button("Add")
    if submitted:
        new_row = pd.DataFrame([{
            "Date": date,
            "Category": category,
            "Amount": amount,
            "Income/Expense": typ
        }])
        if st.session_state['df'] is None:
            st.session_state['df'] = new_row
        else:
            st.session_state['df'] = pd.concat([st.session_state['df'], new_row], ignore_index=True)
        st.success("Entry added! Now select 'View Analysis' to see insights.")

elif menu == "Current database":
    # 1. Load data once
    conn = sqlite3.connect("expenses.db")
    df = pd.read_sql("SELECT * FROM transactions", conn)
    conn.close()
    st.session_state['df'] = df
    
        
