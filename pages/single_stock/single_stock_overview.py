# pages/single_stock/single_stock_overview.py

import streamlit as st
import pandas as pd
from .utils import (
    get_yf_data,
    get_dolthub_income_statement,
    get_dolthub_balance_sheet_assets,
    get_dolthub_balance_sheet_liabilities,
    get_dolthub_balance_sheet_equity,
    format_num,
    format_ratio,
    safe,
    CASH_FLOW_FIELDS
)

# -------------------------------------------------------------------
# CARD RENDERING
# -------------------------------------------------------------------
def render_card(label, value, color, icon_name):
    icon_url = f"https://raw.githubusercontent.com/phosphor-icons/core/main/assets/regular/{icon_name}.svg"
    
    # Card Glow: Outer glow + Inner subtle glow
    box_shadow = f"0 0 40px {color}50, inset 0 0 20px {color}20"

    # Icon Style: Use mask to color the icon and drop-shadow for glow
    icon_style = (
        f"background-color: {color};"
        f"-webkit-mask-image: url('{icon_url}');"
        f"mask-image: url('{icon_url}');"
        f"-webkit-mask-size: contain;"
        f"mask-size: contain;"
        f"-webkit-mask-repeat: no-repeat;"
        f"mask-repeat: no-repeat;"
        f"mask-position: center;"
        f"filter: drop-shadow(0 0 6px {color});"
    )

    return f"""
<div class="neon-card" style="border-color:{color}; box-shadow: {box_shadow};">
<div class="card-content">
<div class="card-icon-wrapper">
<div class="card-icon" style="{icon_style}"></div>
</div>
<div class="card-text-group">
<div class="card-label">{label}</div>
<div class="card-value">{value}</div>
</div>
</div>
</div>
"""

# -------------------------------------------------------------------
# Inject CSS
# -------------------------------------------------------------------
def inject_overview_css():
    st.markdown("""
<style>

.neon-card {
    background-color: #151922;
    border-radius: 16px;
    padding: 12px 18px;
    border: 2px solid transparent;
    display: flex;
    align-items: center;
    min-height: 78px;
    margin-bottom: 16px;
    transition: transform 0.12s ease, filter 0.12s ease;
}
.neon-card:hover {
    transform: translateY(-2px);
    filter: brightness(1.50);
}

.card-content { display: flex; align-items: center; }

.card-icon-wrapper {
    width: 34px;
    height: 34px;
    margin-right: 14px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.card-icon { width: 28px; height: 28px; opacity: 0.9; }

.card-text-group { display: flex; flex-direction: column; }

.card-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #9aa3b3;
    text-transform: uppercase;
    margin-bottom: 1px;
}

.card-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Main Overview Output
# -------------------------------------------------------------------
def display_overview(ticker):
    if not ticker:
        st.info("Please enter a stock ticker.")
        return

    inject_overview_css()

    yf_df, info = get_yf_data(ticker)
    dolt_df = get_dolthub_income_statement(ticker.upper())

    dolt_error = None
    if isinstance(dolt_df, str) and dolt_df.startswith("ERROR::"):
        dolt_error = dolt_df.replace("ERROR::", "")
        dolt_df = pd.DataFrame()

    using_dolthub = not dolt_df.empty

    st.subheader(f"{info.get('shortName', ticker.upper())} ({ticker.upper()})")
    st.caption(f"**Data Source:** {'📦 DoltHub (EDGAR)' if using_dolthub else '🌐 Yahoo Finance'}")
    if dolt_error:
        st.warning(f"DoltHub error: {dolt_error} (fallback to Yahoo Finance)")

    # ROW 1
    row1 = st.columns(3)
    row1[0].markdown(render_card("Sector", safe(info,"sector"), "#2A4E96", "factory"), unsafe_allow_html=True)
    row1[1].markdown(render_card("Industry", safe(info,"industry"), "#2A4E96", "buildings"), unsafe_allow_html=True)
    row1[2].markdown(render_card("Country", safe(info,"country"), "#2A4E96", "globe"), unsafe_allow_html=True)

    # ROW 2
    row2 = st.columns(3)
    row2[0].markdown(render_card("Market Cap", format_num(info.get("marketCap")), "#1AA3A3", "currency-dollar"), unsafe_allow_html=True)
    row2[1].markdown(render_card("Current Price", format_num(info.get("currentPrice")), "#1AA3A3", "chart-line-up"), unsafe_allow_html=True)
    row2[2].markdown(render_card("Beta", format_ratio(info.get("beta")), "#1AA3A3", "scales"), unsafe_allow_html=True)

    # ROW 3
    row3 = st.columns(3)
    row3[0].markdown(render_card("P/E Ratio", format_ratio(info.get("trailingPE")), "#7B3F99", "trend-up"), unsafe_allow_html=True)
    row3[1].markdown(render_card("P/S Ratio", format_ratio(info.get("priceToSalesTrailing12Months")), "#7B3F99", "chart-bar"), unsafe_allow_html=True)
    row3[2].markdown(render_card("P/B Ratio", format_ratio(info.get("priceToBook")), "#7B3F99", "book-open"), unsafe_allow_html=True)
