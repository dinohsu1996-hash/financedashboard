from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from app.services.economic_utils import get_macro_data, synthesize_indicator_conclusion
import json

router = APIRouter()

class MacroRequest(BaseModel):
    series_id: str
    label: str
    years: int = 2

class SynthesisRequest(BaseModel):
    grouped_indicators: Dict[str, List[List[str]]] # List of [label, series_id, unit]
    analysis_focus: str

@router.post("/macro/data")
def fetch_macro_data(request: MacroRequest):
    df = get_macro_data(request.series_id, request.label, request.years)
    if df is None:
        raise HTTPException(status_code=404, detail="Data not found or error fetching data")

    # Convert DataFrame to dict for JSON response
    # We'll use records format: [{'Date': ..., 'Value': ..., 'Series': ...}, ...]
    # Date needs to be stringified
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df.to_dict(orient='records')

@router.post("/macro/synthesize")
def synthesize_macro(request: SynthesisRequest):
    # Convert list of lists to list of tuples as expected by the function
    grouped_tuples = {}
    for group, items in request.grouped_indicators.items():
        grouped_tuples[group] = [tuple(item) for item in items]

    result = synthesize_indicator_conclusion(grouped_tuples, request.analysis_focus)
    return {"conclusion": result}
