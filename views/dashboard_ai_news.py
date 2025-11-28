import streamlit as st
from urllib.parse import urlparse
from src.ai_functions import get_gemini_client, scrape_and_summarize

def render_ai_news_component():
    """
    Renders the AI News widget. 
    Call this function in your main dashboard file.
    """
    st.subheader("☀️ Daily Market Briefing")

    # 1. Initialize Client (Logic from src)
    client = get_gemini_client()

    # 2. UI: Input Section
    # We use an expander so it doesn't clutter the dashboard
    with st.expander("⚙️ Configure News Sources & Topic", expanded=True):
        with st.form("dashboard_news_form"):
            col1, col2 = st.columns([1, 1])
            with col1:
                url_input = st.text_area(
                    "News URLs (one per line):", 
                    value="https://www.cnbc.com/market-insider/\nhttps://finance.yahoo.com/topic/stock-market-news/",
                    height=100
                )
            with col2:
                topic_input = st.text_input(
                    "Focus Topic:", 
                    value="Market Open & Key Movers"
                )
            
            submitted = st.form_submit_button("Generate Briefing")

    # 3. Logic: Handle Submission
    if submitted and client:
        urls_to_scrape = [u.strip() for u in url_input.split('\n') if u.strip()]
        if urls_to_scrape:
            # Call the backend logic
            summary_data = scrape_and_summarize(urls_to_scrape, topic_input, client)
            # Save to session state so it persists across re-runs
            st.session_state['dash_summary'] = summary_data

    # 4. UI: Display Results
    if 'dash_summary' in st.session_state:
        data = st.session_state['dash_summary']
        st.divider()
        st.caption(f"Last updated: {data.get('timestamp', 'N/A')}")
        
        # Grid Layout
        cols = st.columns(2)
        idx = 0
        
        for url, summary in data.items():
            if url != 'timestamp':
                with cols[idx % 2]:
                    with st.container(border=True):
                        # --- EXTRACT SOURCE NAME ---
                        try:
                            # Parse the URL to get the domain (e.g., www.cnbc.com)
                            parsed = urlparse(url)
                            # Clean it up: remove 'www.' and remove the TLD (like .com)
                            # rsplit('.', 1)[0] takes everything before the last dot
                            source_name = parsed.netloc.replace("www.", "").rsplit('.', 1)[0].upper()
                        except:
                            source_name = "SOURCE"

                        # Display the name: Smaller (caption) and linked
                        st.caption(f"🔗 [{source_name}]({url})")
                        st.markdown(summary)
                idx += 1