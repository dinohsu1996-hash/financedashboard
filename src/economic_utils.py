import streamlit as st
from fredapi import Fred
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
# Import your existing scraper to read CME data
from src.ai_functions import scrape_and_summarize, get_gemini_client

@st.cache_resource
def get_fred_client():
    try:
        return Fred(api_key=st.secrets["FRED_API_KEY"])
    except KeyError:
        st.error("🔒 FRED API Key not found. Add FRED_API_KEY to secrets.toml")
        return None

@st.cache_data(ttl=86400)
def get_macro_data(series_id, label, years=2):
    """
    Fetches economic data series from FRED.
    """
    fred = get_fred_client()
    if not fred: return None

    try:
        # Calculate start date
        start_date = datetime.now() - timedelta(days=years*365)
        
        # Fetch data
        data = fred.get_series(series_id, observation_start=start_date)
        df = pd.DataFrame(data, columns=['Value'])
        df.index.name = 'Date'
        df.reset_index(inplace=True)
        df['Series'] = label
        return df
    except Exception as e:
        st.error(f"Error fetching {series_id}: {e}")
        return None

@st.cache_data(ttl=43200) # Cache for 12 hours
def get_cme_fedwatch_update(_client):
    """
    Uses the AI Scraper to read the CME FedWatch tool page and extract probabilities.
    """
    url = "https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html"
    
    # We use a very specific prompt for the AI
    prompt_topic = (
        "Current Federal Reserve Target Rate Probabilities for the UPCOMING meeting only. "
        "Extract the meeting date and the percentages for 'Unchanged', 'Hike', or 'Cut'."
    )
    
    # Reuse your existing robust scraper
    result_dict = scrape_and_summarize([url], prompt_topic, _client)
    
    # Return the text result from the single URL
    return result_dict.get(url, "Could not fetch CME data.")