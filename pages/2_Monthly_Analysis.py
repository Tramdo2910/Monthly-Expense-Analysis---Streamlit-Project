import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import altair as alt

st.title("Analyze Transactions by Month")

if 'df' not in st.session_state or st.session_state['df'] is None or st.session_state['df'].empty:
    st.info("No data available yet. Please upload or enter transactions on the Home page.")
else:
    df = st.session_state['df'].copy()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df.dropna(subset=['Date'], inplace=True)
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)

    months = df['YearMonth'].sort_values().unique()
    selected_month = st.selectbox("Select Month to See Overview", [""] + list(months), index=0)
    # Filter by month
    df_month = df[df['YearMonth'] == selected_month]

    # Only analyze if a month is chosen (not the blank option)
    if selected_month:

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

