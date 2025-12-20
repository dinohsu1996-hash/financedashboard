import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# We will try to use the DoltHub database if available, but since I can't confirm the DB setup
# in this migration environment, I will focus on making sure the code is robust to failures
# and falls back or returns errors gracefully.
# The original code uses root@localhost:3307/earnings.

def get_db_engine():
    try:
        # Assuming the env might provide DB details in future, but hardcoding for now as per original
        # Or better, we just don't crash if it fails.
        return create_engine("mysql+pymysql://root@localhost:3307/earnings")
    except:
        return None

def get_dolthub_data(query: str):
    engine = get_db_engine()
    if not engine:
        return None
    try:
        return pd.read_sql(query, con=engine)
    except Exception as e:
        print(f"DoltHub Error: {e}")
        return None

def get_stock_overview(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        # Fast info usually works, but fallback to .info if needed
        # .info is sometimes slow or rate limited
        info = stock.info

        # Check if we got valid info. yfinance might return an empty dict or minimal info if not found
        # but it doesn't always raise an exception.
        # Often checking 'symbol' or 'regularMarketPrice' helps.
        if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info and 'longName' not in info):
             # It might be an invalid ticker
             return None

        # Basic Price Data
        # hist = stock.history(period="1d")
        # current_price = hist['Close'].iloc[-1] if not hist.empty else None

        return {
            "name": info.get("longName"),
            "ticker": ticker.upper(),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "description": info.get("longBusinessSummary"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "currency": info.get("currency", "USD"),
            "website": info.get("website"),
            "logo_url": info.get("logo_url") # yfinance sometimes has this
        }
    except Exception as e:
        print(f"Overview Error: {e}")
        return None

def get_stock_history(ticker: str, period="1y", interval="1d"):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            return []

        hist.reset_index(inplace=True)
        # Convert to list of dicts: { date: '...', open: ..., high: ..., low: ..., close: ..., volume: ... }
        return hist.apply(lambda row: {
            "date": row['Date'].strftime('%Y-%m-%d'),
            "open": row['Open'],
            "high": row['High'],
            "low": row['Low'],
            "close": row['Close'],
            "volume": row['Volume']
        }, axis=1).tolist()
    except Exception as e:
        print(f"History Error: {e}")
        return []

def get_financials(ticker: str, statement_type: str = "income", source: str = "dolthub"):
    # statement_type: income, balance_sheet_assets, balance_sheet_liabilities, balance_sheet_equity, cash_flow

    if source == "dolthub":
        table_map = {
            "income": "income_statement",
            "balance_sheet_assets": "balance_sheet_assets",
            "balance_sheet_liabilities": "balance_sheet_liabilities",
            "balance_sheet_equity": "balance_sheet_equity",
            "cash_flow": "cash_flow_statement"
        }

        table = table_map.get(statement_type)
        if table:
            query = f"SELECT * FROM {table} WHERE act_symbol = '{ticker.upper()}' ORDER BY date DESC;"
            df = get_dolthub_data(query)
            if df is not None and not df.empty:
                # Convert Date to string
                if 'date' in df.columns:
                    df['date'] = df['date'].astype(str)
                return df.to_dict(orient='records')

    # Fallback to Yahoo Finance (simplified)
    # yfinance returns data in a different format, so we might need to normalize it if we want consistent frontend handling.
    # For now, let's just return what yfinance gives but formatted nicely.
    try:
        stock = yf.Ticker(ticker)
        if statement_type == "income":
            df = stock.financials
        elif "balance_sheet" in statement_type:
            df = stock.balance_sheet
        elif statement_type == "cash_flow":
            df = stock.cashflow
        else:
            return []

        if df.empty:
            return []

        # Transpose so dates are rows? or keep as is?
        # Usually easier if dates are keys or array of objects.
        # Let's return as a dictionary where keys are metric names and values are objects with dates.
        # Or better: List of objects, each object is a period (column in yf df)

        # YF structure: Columns are Dates, Rows are Metrics

        # Let's convert to:
        # [ { date: "2023-12-31", "Total Revenue": 1000, ... }, ... ]

        df_T = df.T
        df_T.index.name = "date"
        df_T.reset_index(inplace=True)
        df_T['date'] = df_T['date'].astype(str)
        return df_T.to_dict(orient='records')

    except Exception as e:
        print(f"YFinance Financials Error: {e}")
        return []
