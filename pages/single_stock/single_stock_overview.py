# pages/single_stock/single_stock_overview.py

import streamlit as st
import pandas as pd

from .utils import (
    get_yf_data,
    get_dolthub_income_statement,
    get_dolthub_balance_sheet_assets,
    get_dolthub_balance_sheet_liabilities,
    get_dolthub_balance_sheet_equity,
    render_card,
    format_num,
    format_ratio,
    safe,
    CASH_FLOW_FIELDS
)

def display_overview(ticker):
    if not ticker:
        st.info("Please select a stock ticker.")
        return

    # Load Yahoo Finance Data
    yf_df, info = get_yf_data(ticker)

    # Load DoltHub Income Statement
    dolt_df = get_dolthub_income_statement(ticker.upper())
    dolt_error = None
    if isinstance(dolt_df, str) and dolt_df.startswith("ERROR::"):
        dolt_error = dolt_df.replace("ERROR::", "")
        dolt_df = pd.DataFrame()

    using_dolthub = not dolt_df.empty

    # Load Balance Sheet Data
    get_dolthub_balance_sheet_assets(ticker.upper())
    get_dolthub_balance_sheet_liabilities(ticker.upper())
    get_dolthub_balance_sheet_equity(ticker.upper())

    # Prepare cash flow column display
    available_meta = [col for col in ["date", "period", "act_symbol"] if col in dolt_df.columns]
    available_cash_cols = [col for col in CASH_FLOW_FIELDS if col in dolt_df.columns]
    _ = dolt_df[available_meta + available_cash_cols].copy()

    # UI Rendering
    st.subheader(f"{info.get('shortName', ticker.upper())} ({ticker.upper()})")
    st.caption(f"**Data Source:** {'📦 DoltHub (EDGAR)' if using_dolthub else '🌐 Yahoo Finance'}")
    if dolt_error:
        st.warning(f"DoltHub error: {dolt_error} (falling back to Yahoo Finance)")

    # Company Info Section
    row1 = st.columns(3)
    row1[0].markdown(render_card("Sector", safe(info, "sector"), "#2A4E96"), unsafe_allow_html=True)
    row1[1].markdown(render_card("Industry", safe(info, "industry"), "#2A4E96"), unsafe_allow_html=True)
    row1[2].markdown(render_card("Country", safe(info, "country"), "#2A4E96"), unsafe_allow_html=True)

    # Overview Metrics
    row2 = st.columns(3)
    row2[0].markdown(render_card("Market Cap", format_num(info.get("marketCap")), "#1AA3A3"), unsafe_allow_html=True)
    row2[1].markdown(render_card("Current Price", format_num(info.get("currentPrice")), "#1AA3A3"), unsafe_allow_html=True)
    row2[2].markdown(render_card("Beta", format_ratio(info.get("beta")), "#1AA3A3"), unsafe_allow_html=True)

    # Valuation Metrics
    row3 = st.columns(3)
    row3[0].markdown(render_card("P/E Ratio", format_ratio(info.get("trailingPE")), "#7B3F99"), unsafe_allow_html=True)
    row3[1].markdown(render_card("P/S Ratio", format_ratio(info.get("priceToSalesTrailing12Months")), "#7B3F99"), unsafe_allow_html=True)
    row3[2].markdown(render_card("P/B Ratio", format_ratio(info.get("priceToBook")), "#7B3F99"), unsafe_allow_html=True)
