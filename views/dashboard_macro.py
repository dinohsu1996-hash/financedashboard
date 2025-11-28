import streamlit as st
import plotly.express as px
from src.economic_utils import get_macro_data, get_cme_fedwatch_update
from src.ai_functions import get_gemini_client

def render_macro_economic_section():
    st.markdown("### 🏦 Macroeconomic Indicators & Fed Policy")
    
    # --- 1. CME FedWatch Section (AI Powered) ---
    client = get_gemini_client()
    
    # Display in an expander or a highlighted box
    with st.container(border=True):
        col_fed, col_graph = st.columns([1, 2])
        
        with col_fed:
            st.markdown("#### 🦅 CME FedWatch Insights")
            if client:
                with st.spinner("Analyzing FedWatch Tool..."):
                    fed_summary = get_cme_fedwatch_update(client)
                    st.markdown(fed_summary)
                    st.caption("Source: CME Group (AI Analyzed)")
            else:
                st.warning("Gemini Client not initialized.")

        # --- 2. FRED Data Graphs ---
        with col_graph:
            # Dropdown to select which graph to show
            graph_option = st.selectbox(
                "Select Economic Indicator:",
                [
                    ("Federal Funds Rate", "FEDFUNDS"),
                    ("10-Year Treasury Yield", "DGS10"),
                    ("US Core Inflation (CPI)", "CPILFESL"),
                    ("Unemployment Rate", "UNRATE"),
                    ("M2 Money Supply", "M2SL")
                ],
                format_func=lambda x: x[0]
            )
            
            label, series_id = graph_option
            
            # Fetch Data
            df = get_macro_data(series_id, label)
            
            if df is not None:
                # Create a clean line chart
                fig = px.line(df, x='Date', y='Value', title=f"{label} (Last 2 Years)")
                fig.update_layout(
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300,
                    xaxis_title=None,
                    yaxis_title=None
                )
                st.plotly_chart(fig, use_container_width=True)