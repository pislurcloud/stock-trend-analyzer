import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from core.full_pipeline import run_full_analysis

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Stock Trend Analyzer",
    layout="centered"
)

# -----------------------------
# Header
# -----------------------------
st.title("📈 Stock Trend Analyzer")
st.caption(
    "Investor-friendly, historical trend analysis using AI. "
    "This tool provides analytical insights only — not investment advice."
)

# -----------------------------
# Sidebar (minimal MVP)
# -----------------------------
st.sidebar.header("Analysis Settings")

ticker = st.sidebar.text_input(
    "Stock Ticker",
    value="AAPL",
    help="Enter a valid stock ticker (e.g., AAPL, MSFT, INFY)"
)

years = st.sidebar.slider(
    "Analysis Period (Years)",
    min_value=5,
    max_value=15,
    value=10,
    step=1
)

run_button = st.sidebar.button("Run Analysis")

# -----------------------------
# Main execution
# -----------------------------
if run_button:
    if not ticker.strip():
        st.error("Please enter a valid stock ticker.")
    else:
        with st.spinner("Running analysis… this may take 30–60 seconds"):
            try:
                result = run_full_analysis(
                    ticker=ticker.strip().upper(),
                    years=years
                )

                # -----------------------------
                # Executive Summary
                # -----------------------------
                st.subheader("Executive Summary")
                st.write(result.get("exec_summary", "No summary generated."))

                # -----------------------------
                # Final Investor Narrative
                # -----------------------------
                st.subheader("Detailed Analysis")
                st.write(result.get("final_narrative", "No narrative generated."))

                # -----------------------------
                # Diagnostics (collapsible)
                # -----------------------------
                with st.expander("Technical Details (for transparency)"):
                    st.json({
                        "Ticker": result["ticker"],
                        "Period": result["analysis_period"],
                        "Dominant Trend": result["dominant_trend"],
                        "Confidence": result["trend_confidence"],
                        "Recent Trend": result["recent_trend"],
                        "Trend Distribution": result["trend_distribution"]
                    })

            except Exception as e:
                st.error("Analysis failed.")
                st.exception(e)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption(
    "⚠️ Disclaimer: This analysis is historical and informational only. "
    "It does not constitute investment advice or recommendations."
)
