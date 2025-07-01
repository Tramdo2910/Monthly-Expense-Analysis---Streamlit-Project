import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import altair as alt

st.title("Analyze Transactions by Month")

# Load data
conn = sqlite3.connect("expenses.db")
df = pd.read_sql("SELECT * FROM transactions", conn)
conn.close()

# Check your column names!
col_tag = 'Income/Expense'
date_col = 'Date'

# Parse the main df dates and YearMonth if not done already
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
df.dropna(subset=[date_col], inplace=True)
df['YearMonth'] = df[date_col].dt.to_period('M').astype(str)


# Let user select month to analyze
months = df['YearMonth'].sort_values().unique()
selected_month = st.selectbox("Select Month", months)

month_df = df[df['YearMonth'] == selected_month]

# Filter by month
df_month = df[df['YearMonth'] == selected_month]

# Compute income and expense
income = df_month[df_month[col_tag].str.lower() == 'income']['Amount'].sum()
expense = df_month[df_month[col_tag].str.lower() == 'expense']['Amount'].sum()
remaining = income - expense

# Display
st.markdown(f"### Income for {selected_month}: <span style='color:green'>${income:,.2f}</span>", unsafe_allow_html=True)
st.markdown(f"### Expenses for {selected_month}: <span style='color:red'>${expense:,.2f}</span>", unsafe_allow_html=True)

if remaining >= 0:
    st.markdown(f"### Remaining Fund: <span style='color:green'>${remaining:,.2f}</span>", unsafe_allow_html=True)
else:
    st.markdown(f"### Remaining Fund: <span style='color:red'>${remaining:,.2f}</span>", unsafe_allow_html=True)
st.subheader(f"Transactions for {selected_month}")
st.dataframe(df_month, use_container_width=True)

# Group by category for the selected month
cat_data = df_month[df_month[col_tag].str.lower() == 'expense'].groupby('Category')['Amount'].sum()

st.subheader("Expense Share by Category")
if not cat_data.empty:
    # --- PIE CHART WITH PERCENTAGES IN LEGEND ONLY ---
    fig, ax = plt.subplots()

    # Calculate percentages for legend
    percentages = 100 * cat_data / cat_data.sum()
    labels_with_pct = [f"{cat} ({pct:.1f}%)" for cat, pct in zip(cat_data.index, percentages)]

    wedges, _ = ax.pie( # type: ignore
        cat_data,
        labels=None,
        startangle=90,
        counterclock=False
    )
    ax.axis('equal')
    ax.legend(
        wedges,
        labels_with_pct,
        title="Category",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize='small'
    )
    st.pyplot(fig)

    # --- HORIZONTAL BAR CHART ---
    st.subheader("Expense by Category")
    fig2, ax2 = plt.subplots()
    cat_data.sort_values().plot(kind='barh', ax=ax2, color='skyblue')
    ax2.set_xlabel("Amount Spent")
    ax2.set_ylabel("Category")
    ax2.set_title("Spending by Category")
    st.pyplot(fig2) 
else:
    st.info("No expense data for this month.")

st.subheader("Total Spent This Month: $%.2f" % df_month[df_month[col_tag].str.lower() == 'expense']['Amount'].sum())

