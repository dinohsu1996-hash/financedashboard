import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from pages.single_stock.utils import (
    get_dolthub_income_statement,
    get_dolthub_balance_sheet_assets,
    get_dolthub_balance_sheet_liabilities,
    get_dolthub_balance_sheet_equity,
    get_dolthub_cash_flow,
    get_historical_data,
    format_num,
    CASH_FLOW_FIELDS
)

st.set_page_config(page_title="Comparison Mode", page_icon="⚖️", layout="wide")

st.title("⚖️ Comparison Mode")
st.markdown("Compare financial performance and stock price action across multiple companies.")

# --- Sidebar Controls ---
st.sidebar.header("Comparison Settings")

# Ticker Selection
# Default to a few popular tech stocks for demo purposes
default_tickers = ["AAPL", "MSFT", "GOOG"]
selected_tickers = st.sidebar.multiselect(
    "Select Companies (Tickers)",
    options=default_tickers + ["AMZN", "TSLA", "NVDA", "META", "NFLX"], # Add more suggestions or make it open
    default=default_tickers
)

# Allow user to add custom tickers if not in list (by typing in multiselect if configured, 
# but standard multiselect restricts to options. Let's add a text input for custom ones or just rely on user typing if we use a different widget. 
# For now, standard multiselect with a predefined list + ability to add is tricky without a separate input. 
# Let's just add a text input to add to the list.)
new_ticker = st.sidebar.text_input("Add Ticker manually (e.g. JPM)")
if new_ticker:
    upper_ticker = new_ticker.upper()
    if upper_ticker not in selected_tickers:
        selected_tickers.append(upper_ticker)

if not selected_tickers:
    st.warning("Please select at least one company to compare.")
    st.stop()

# Period Selection
statement_period = st.sidebar.selectbox("Statement Period", ["Annual", "Quarterly"])

# --- Price Performance Chart ---
st.subheader("📈 Price Performance Comparison")

chart_period = st.selectbox("Chart Range", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

@st.cache_data(ttl=3600)
def get_multi_stock_data(tickers, period):
    data = {}
    for t in tickers:
        hist = get_historical_data(t, period=period)
        if not hist.empty:
            data[t] = hist["Close"]
    return pd.DataFrame(data)

price_df = get_multi_stock_data(selected_tickers, chart_period)

if not price_df.empty:
    # Normalize to % change starting at 0
    normalized_df = (price_df / price_df.iloc[0] - 1) * 100
    
    fig = go.Figure()
    for col in normalized_df.columns:
        fig.add_trace(go.Scatter(
            x=normalized_df.index,
            y=normalized_df[col],
            mode='lines',
            name=col
        ))
    
    fig.update_layout(
        title=f"Relative Price Performance ({chart_period})",
        xaxis_title="Date",
        yaxis_title="% Change",
        hovermode="x unified",
        template="plotly_dark",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No price data available for the selected tickers.")

# --- Financial Comparisons ---
st.markdown("---")
st.subheader("📊 Financial Statement Comparison")

tabs = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow", "Key Ratios"])

# Helper to fetch and align data
def fetch_latest_financials(tickers, period_type, statement_type):
    """
    Fetches the latest available data for the given period type (Annual/Quarterly).
    Returns a DataFrame where columns are Tickers and rows are Metrics.
    """
    combined_data = {}
    
    period_filter = "YEAR" if period_type == "Annual" else "QUARTER"
    
    for t in tickers:
        df = None
        if statement_type == "income":
            df = get_dolthub_income_statement(t)
        elif statement_type == "balance_assets":
            df = get_dolthub_balance_sheet_assets(t)
        elif statement_type == "balance_liabilities":
            df = get_dolthub_balance_sheet_liabilities(t)
        elif statement_type == "balance_equity":
            df = get_dolthub_balance_sheet_equity(t)
        elif statement_type == "cash_flow":
            df = get_dolthub_cash_flow(t)
            
        if isinstance(df, pd.DataFrame) and not df.empty:
            # Filter by period
            if "period" in df.columns:
                df = df[df["period"].astype(str).str.upper() == period_filter]
            
            # Sort by date desc and take top 1 (latest)
            # Note: This compares the *latest available* report. 
            # Ideally we align by year/quarter, but for a quick comparison view, latest is standard.
            if not df.empty:
                df = df.sort_values("date", ascending=False)
                latest = df.iloc[0]
                combined_data[t] = latest
    
    if not combined_data:
        return pd.DataFrame()
        
    return pd.DataFrame(combined_data)

# Helper for styling
def style_comparison_table(df):
    """
    Applies styling to comparison tables:
    - Highlights maximum value in each row (green)
    - Formats numbers
    """
    def highlight_max(s):
        '''
        Highlight the maximum in a Series yellow.
        '''
        is_max = s == s.max()
        return ['background-color: #2E7D32; color: white' if v else '' for v in is_max]

    # We need to convert to numeric for highlighting, but keep formatting for display
    # This is tricky with pandas style. 
    # Strategy: Use style.apply on numeric data, and style.format for display.
    
    return df.style.apply(highlight_max, axis=1).format(lambda x: format_num(x) if pd.notnull(x) else "—")

# --- Income Statement Tab ---
with tabs[0]:
    st.markdown(f"### Latest {statement_period} Income Statement")
    
    df_income = fetch_latest_financials(selected_tickers, statement_period, "income")
    
    if not df_income.empty:
        rows_to_drop = ["act_symbol", "period", "date", "cik"]
        df_income_clean = df_income.drop([r for r in rows_to_drop if r in df_income.index], errors="ignore")
        df_income_clean.index = df_income_clean.index.str.replace("_", " ").str.title()
        
        st.dataframe(style_comparison_table(df_income_clean), use_container_width=True)
    else:
        st.info("No income statement data found.")

# --- Balance Sheet Tab ---
with tabs[1]:
    st.markdown(f"### Latest {statement_period} Balance Sheet")
    
    st.markdown("#### Assets")
    df_assets = fetch_latest_financials(selected_tickers, statement_period, "balance_assets")
    if not df_assets.empty:
        rows_to_drop = ["act_symbol", "period", "date", "cik"]
        df_clean = df_assets.drop([r for r in rows_to_drop if r in df_assets.index], errors="ignore")
        df_clean.index = df_clean.index.str.replace("_", " ").str.title()
        st.dataframe(style_comparison_table(df_clean), use_container_width=True)
        
    st.markdown("#### Liabilities")
    df_liab = fetch_latest_financials(selected_tickers, statement_period, "balance_liabilities")
    if not df_liab.empty:
        rows_to_drop = ["act_symbol", "period", "date", "cik"]
        df_clean = df_liab.drop([r for r in rows_to_drop if r in df_liab.index], errors="ignore")
        df_clean.index = df_clean.index.str.replace("_", " ").str.title()
        st.dataframe(style_comparison_table(df_clean), use_container_width=True)

    st.markdown("#### Equity")
    df_eq = fetch_latest_financials(selected_tickers, statement_period, "balance_equity")
    if not df_eq.empty:
        rows_to_drop = ["act_symbol", "period", "date", "cik"]
        df_clean = df_eq.drop([r for r in rows_to_drop if r in df_eq.index], errors="ignore")
        df_clean.index = df_clean.index.str.replace("_", " ").str.title()
        st.dataframe(style_comparison_table(df_clean), use_container_width=True)

# --- Cash Flow Tab ---
with tabs[2]:
    st.markdown(f"### Latest {statement_period} Cash Flow")
    
    df_cf = fetch_latest_financials(selected_tickers, statement_period, "cash_flow")
    
    if not df_cf.empty:
        available_fields = [f for f in CASH_FLOW_FIELDS if f in df_cf.index]
        rows_to_drop = ["act_symbol", "period", "date", "cik"]
        df_cf_clean = df_cf.drop([r for r in rows_to_drop if r in df_cf.index], errors="ignore")
        df_cf_clean.index = df_cf_clean.index.str.replace("_", " ").str.title()
        
        st.dataframe(style_comparison_table(df_cf_clean), use_container_width=True)
    else:
        st.info("No cash flow data found.")

# --- Ratios Tab ---
with tabs[3]:
    st.markdown(f"### Key Ratios ({statement_period})")
    
    # We need to fetch all statements for each ticker to calculate ratios
    ratios_data = {}
    
    for t in selected_tickers:
        # Fetch all needed data
        dolt_df = get_dolthub_income_statement(t)
        assets_df = get_dolthub_balance_sheet_assets(t)
        liab_df = get_dolthub_balance_sheet_liabilities(t)
        equity_df = get_dolthub_balance_sheet_equity(t)
        cash_df = get_dolthub_cash_flow(t)
        
        if any(df is None or df.empty for df in [dolt_df, assets_df, liab_df, equity_df]):
            continue
            
        # Filter and merge latest
        period_filter = "YEAR" if statement_period == "Annual" else "QUARTER"
        
        try:
            # Helper to get latest period row
            def get_latest(df):
                if "period" in df.columns:
                    df = df[df["period"].astype(str).str.upper() == period_filter]
                return df.sort_values("date", ascending=False).iloc[0] if not df.empty else None

            latest_inc = get_latest(dolt_df)
            latest_assets = get_latest(assets_df)
            latest_liab = get_latest(liab_df)
            latest_eq = get_latest(equity_df)
            latest_cf = get_latest(cash_df) if cash_df is not None else None
            
            if latest_inc is None or latest_assets is None or latest_liab is None or latest_eq is None:
                continue
                
            # Calculate Ratios
            # Safe get helper
            def get_val(series, key):
                return float(series.get(key, 0))
                
            net_income = get_val(latest_inc, "net_income")
            sales = get_val(latest_inc, "sales")
            cogs = get_val(latest_inc, "cost_of_goods")
            total_assets = get_val(latest_assets, "total_assets")
            total_equity = get_val(latest_eq, "total_equity")
            total_liab = get_val(latest_liab, "total_liabilities")
            pretax_income = get_val(latest_inc, "pretax_income")
            interest_expense = get_val(latest_inc, "interest_expense")
            
            ratios = {}
            
            # Profitability
            ratios["Net Profit Margin"] = (net_income / sales) if sales else 0
            ratios["Gross Margin"] = ((sales - cogs) / sales) if sales else 0
            ratios["ROA"] = (net_income / total_assets) if total_assets else 0
            ratios["ROE"] = (net_income / total_equity) if total_equity else 0
            
            # Solvency
            ratios["Debt to Equity"] = (total_liab / total_equity) if total_equity else 0
            ratios["Debt Ratio"] = (total_liab / total_assets) if total_assets else 0
            ratios["Equity Ratio"] = (total_equity / total_assets) if total_assets else 0
            ratios["Interest Coverage"] = (pretax_income / interest_expense) if interest_expense else 0
            
            if latest_cf is not None:
                ocf = get_val(latest_cf, "net_cash_from_operating_activities")
                curr_liab = get_val(latest_liab, "current_liabilities")
                ratios["Operating Cash Flow Ratio"] = (ocf / curr_liab) if curr_liab else 0
            
            ratios_data[t] = ratios
            
        except Exception as e:
            # st.error(f"Error calculating ratios for {t}: {e}")
            continue

    if ratios_data:
        df_ratios = pd.DataFrame(ratios_data)
        
        # Format Ratios
        percent_rows = ["Net Profit Margin", "Gross Margin", "ROA", "ROE", "Debt Ratio", "Equity Ratio"]
        
        def format_ratio_val(val, row_name):
            if row_name in percent_rows:
                return f"{val * 100:.2f}%"
            return f"{val:.2f}"
            
        # Apply formatting
        # We can't easily apply different formats to different rows in a standard dataframe display without style
        # So we'll convert to string for display or use style
        
        st.dataframe(df_ratios.style.format(lambda x: f"{x:.2f}"), use_container_width=True)
        
        # Better styling: Highlight best/worst?
        # For margins/returns, higher is green. For debt, lower is often better (but depends).
        # Let's just stick to a simple heatmap style for now.
        
        st.caption("Green indicates higher values, Red indicates lower values (relative to row).")
        
        def highlight_max(s):
            is_max = s == s.max()
            return ['background-color: #2E7D32' if v else '' for v in is_max]
            
        # st.dataframe(df_ratios.style.apply(highlight_max, axis=1), use_container_width=True)
        
    else:
        st.info("Could not calculate ratios for selected tickers.")
