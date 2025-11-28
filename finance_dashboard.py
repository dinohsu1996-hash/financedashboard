import asyncio
import sys

# --- 🔧 WINDOWS FIX for Playwright ---
# This forces Windows to use the correct Event Loop for running subprocesses (like the browser)
# This MUST be done before importing streamlit or any other library
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
# -------------------------------------

import streamlit as st
from streamlit_option_menu import option_menu
import os

# --- IMPORT UI COMPONENTS ---
from views.dashboard_ai_news import render_ai_news_component
from views.dashboard_macro import render_macro_economic_section

# -----------------------------------------------
# 🎯 Load ticker list from file
def load_ticker_list(filepath="all_tickers.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tickers = [line.strip() for line in f if line.strip()]
        return tickers
    except FileNotFoundError:
        return []

ticker_list = load_ticker_list()
# -----------------------------------------------

# 🛠 Page config
st.set_page_config(layout="wide", page_title="Finance Dashboard", initial_sidebar_state="collapsed")

# 🔒 Hide sidebar
hide_sidebar_style = """
    <style>
        section[data-testid="stSidebar"] { display: none; }
        div[data-testid="stAppViewContainer"] { margin-left: 0px; }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# 🧠 App title
st.title("📊 Finance Dashboard")

# 🔘 Menu
selected = option_menu(
    menu_title=None,
    options=["Dashboard", "Personal Finance", "Single Stock", "Comparison", "Analysis"],
    icons=["house-door", "graph-up", "columns-gap", "columns-gap", "file-earmark-bar-graph"],
    orientation="horizontal",
    default_index=0
)

# 🔁 Helper to load page scripts safely
def run_script(path):
    if not path.startswith("pages"):
        full_path = os.path.join("pages", path)
    else:
        full_path = path

    if os.path.exists(full_path):
        with open(full_path, encoding="utf-8") as f:
            code = f.read()
        exec(code, globals())
    else:
        st.error(f"Missing file: {full_path}")

# ==========================================
# 🧩 Page Logic
# ==========================================

if selected == "Dashboard":
    # This is now the ONLY line needed to show the AI News section
    render_ai_news_component()
    st.divider() # Visual separator
    
    # 2. NEW Macro Section
    render_macro_economic_section()

elif selected == "Personal Finance":
    run_script("1_Personal_Finance.py")

elif selected == "Single Stock":
    run_script("single_stock/main.py")

elif selected == "Comparison":
    run_script("3_Comparison_Mode.py")

elif selected == "Analysis":
    run_script("4_Analysis_Mode.py")