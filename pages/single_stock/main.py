# main.py

import streamlit as st
import pandas as pd

from pages.single_stock.single_stock_overview import display_overview, get_yf_data
from pages.single_stock.single_stock_fundamentals import display_fundamentals
from pages.single_stock.single_stock_charts import display_charts
from pages.single_stock.utils import (
    get_dolthub_income_statement,
    get_dolthub_balance_sheet_assets,
    get_dolthub_balance_sheet_liabilities,
    get_dolthub_balance_sheet_equity,
    get_dolthub_cash_flow,
)

# -----------------------------
# Page Setup
# -----------------------------
st.title("📈 Company Overview")

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.metric-card {
    border-radius:10px;
    padding:15px;
    margin-bottom:12px;
    color:white;
    text-align: center;
}
.metric-label {
    font-size:13px;
    opacity:0.85;
}
.metric-value {
    font-size:19px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Ticker Input
# -----------------------------
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, or 2330.TW):").strip().upper()


# -----------------------------
# Display Logic
# -----------------------------
if ticker:
    # Primary source: DoltHub
    dolt_df = get_dolthub_income_statement(ticker)
    using_dolthub = dolt_df is not None and not dolt_df.empty

    # Fallback: Yahoo Finance
    yf_df, _ = get_yf_data(ticker)

    # Overview Section
    with st.expander("Overview", expanded=True):
        display_overview(ticker)

    # Charts Section
    with st.expander("Charts", expanded=True):
        display_charts(ticker, yf_df, dolt_df, using_dolthub)

    # Financial Statements Section
    with st.expander("Financial Statements", expanded=True):
        statement_tab = st.radio(
            "Select Statement:",
            ["Income Statement", "Balance Sheet", "Cash Flow", "Key Ratios"],
            horizontal=True
        )

        if using_dolthub:
            assets_df = get_dolthub_balance_sheet_assets(ticker)
            liabilities_df = get_dolthub_balance_sheet_liabilities(ticker)
            equity_df = get_dolthub_balance_sheet_equity(ticker)

            if assets_df.empty and liabilities_df.empty and equity_df.empty:
                st.warning("📭 No DoltHub financials found. Falling back to Yahoo Finance.")
                using_dolthub = False

        # Unified fundamentals rendering
        display_fundamentals(
            statement_tab=statement_tab,
            statement_period="Annual",
            dolt_df=dolt_df if using_dolthub else None,
            assets_df=assets_df if using_dolthub else None,
            liabilities_df=liabilities_df if using_dolthub else None,
            equity_df=equity_df if using_dolthub else None,
            get_dolthub_cash_flow=get_dolthub_cash_flow if using_dolthub else None,
            ticker=ticker,
            yf_df=None if using_dolthub else yf_df,
        )
else:
    st.info("Please enter a stock ticker to view its information.")
