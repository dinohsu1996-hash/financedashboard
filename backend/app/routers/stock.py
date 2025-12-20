from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.services.stock.stock_services import get_stock_overview, get_stock_history, get_financials

router = APIRouter()

@router.get("/stock/{ticker}/overview")
def stock_overview(ticker: str):
    data = get_stock_overview(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found or error fetching data")
    return data

@router.get("/stock/{ticker}/history")
def stock_history(ticker: str, period: str = "1y", interval: str = "1d"):
    data = get_stock_history(ticker, period, interval)
    # Return empty list is fine if no data, frontend handles it
    return data

@router.get("/stock/{ticker}/financials/{statement_type}")
def stock_financials(ticker: str, statement_type: str, source: str = "dolthub"):
    # statement_type options matches the service: income, balance_sheet_assets, etc.
    # Note: frontend might request "balance_sheet" broadly, we might need to handle that.

    # If the request is just "balance_sheet" and source is yahoo, that works.
    # If source is dolthub, we might need to be specific.

    data = get_financials(ticker, statement_type, source)
    return data
