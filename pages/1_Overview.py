import streamlit as st
import pandas as pd
import sqlite3
import altair as alt

st.title("Income & Expense Analyzer")

if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.info("No data available yet. Please upload or enter transactions on the Home page.")
else:
    #Load data
    df = st.session_state['df'].copy()
    # 2. Check and fix the column name
    col_tag = 'Income/Expense'  # Change to EXACT name from your data
    date_col = 'Date'           # Also change if needed
    
    # 3. Filter income and expense tables
    income_df = df[df[col_tag].str.lower() == 'income'].copy()
    expense_df = df[df[col_tag].str.lower() == 'expense'].copy()
    
    # 4. Standardize date and add YearMonth
    for d in [income_df, expense_df]:
        if date_col in d.columns:
            d[date_col] = pd.to_datetime(d[date_col], errors='coerce')
            d.dropna(subset=[date_col], inplace=True)
            d['YearMonth'] = d[date_col].dt.to_period('M').astype(str)
    
    
    # --- INCOME ANALYSIS ---
    if not income_df.empty:
        st.subheader("Total Income by Month")
        income_month = income_df.groupby('YearMonth')["Amount"].sum().reset_index()
        st.bar_chart(income_month, x='YearMonth', y='Amount')
    
    # --- EXPENSE ANALYSIS ---
    if not expense_df.empty:
        st.subheader("Total Spending by Month")
        expense_month = expense_df.groupby('YearMonth')["Amount"].sum().reset_index()
        st.bar_chart(expense_month, x='YearMonth', y='Amount')
    
        st.subheader("Top Spending Category by Month")
        top_category = (
            expense_df.groupby(['YearMonth', 'Category'])['Amount'].sum()
            .reset_index()
            .sort_values(['YearMonth', 'Amount'], ascending=[True, False])
        )
        top_per_month = top_category.groupby('YearMonth').first().reset_index()
        st.dataframe(top_per_month, use_container_width=True)
    
        st.subheader("Spending per Category Each Month")
        cat_month = expense_df.groupby(['YearMonth', 'Category'])['Amount'].sum().reset_index()
        chart = alt.Chart(cat_month).mark_bar().encode(
            x='YearMonth:N',
            y='Amount:Q',
            color='Category:N',
            tooltip=['Category', 'Amount']
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No expense data found. Please check your table and filter.")
    
    # Show tables
    st.subheader("Income Transactions")
    st.dataframe(income_df, use_container_width=True)
    
    st.subheader("Expense Transactions")
    st.dataframe(expense_df, use_container_width=True)




