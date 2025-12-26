import streamlit as st

from core.analytics_pipeline import run_trend_analysis
from llm.narrative import generate_narrative


# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Stock Performance Snapshot",
    layout="wide",
)

st.title("📈 Stock Performance Snapshot")
st.caption(
    "Historical performance analysis based on price data only. "
    "This tool is informational and does not provide investment advice."
)

# -------------------------------------------------
# Sidebar inputs
# -------------------------------------------------
with st.sidebar:
    st.header("Analysis Settings")

    ticker = st.text_input(
        "Stock Ticker",
        value="AAPL",
        help="Examples: AAPL, MSFT, NVDA, RELIANCE.NS",
    )

    years = st.slider(
        "Lookback Period (Years)",
        min_value=5,
        max_value=15,
        value=10,
        step=1,
    )

    run_button = st.button("Run Analysis")

# -------------------------------------------------
# Run analysis
# -------------------------------------------------
if run_button:
    try:
        snapshot = run_trend_analysis(ticker.strip().upper(), years)

        # =================================================
        # Executive Snapshot
        # =================================================
        st.subheader("📊 Executive Snapshot")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("CAGR", f"{snapshot['growth']['cagr']}%")
        c2.metric("Price Multiple", f"{snapshot['growth']['price_multiple']}×")
        c3.metric("Max Drawdown", f"{snapshot['risk']['max_drawdown']}%")
        c4.metric("Volatility", f"{snapshot['consistency']['annualized_volatility']}%")

        # =================================================
        # Charts
        # =================================================
        st.subheader("📈 Price Performance")
        price_df = snapshot["charts"]["price"].set_index("date")
        st.line_chart(price_df["price"])

        st.subheader("📉 Drawdowns (Pain Index)")
        drawdown_df = snapshot["charts"]["drawdown"].set_index("date")
        st.area_chart(drawdown_df)

        st.subheader("🔄 Rolling 12-Month Returns")
        rolling_df = snapshot["charts"]["rolling_12m"].set_index("date")
        st.line_chart(rolling_df)

        # =================================================
        # Growth vs Risk
        # =================================================
        st.subheader("⚖️ Growth vs Risk")

        left, right = st.columns(2)

        with left:
            st.markdown("**Growth Profile**")
            st.write(f"- Total Return: {snapshot['growth']['total_return_pct']}%")
            st.write(
                f"- Positive Years: "
                f"{int(snapshot['growth']['positive_year_ratio'] * 100)}%"
            )

            if snapshot["summary_flags"]["strong_compounder"]:
                st.success("Strong long-term compounder")

        with right:
            st.markdown("**Risk Profile**")
            st.write(
                f"- Worst 12M Period: "
                f"{snapshot['risk']['worst_rolling_12m']}%"
            )

            if snapshot["summary_flags"]["deep_drawdowns"]:
                st.warning("Experienced deep historical drawdowns")

        # =================================================
        # Investor Narrative
        # =================================================
        st.subheader("📝 Investor Narrative")

        with st.spinner("Generating narrative summary..."):
            narrative = generate_narrative(snapshot)

        if narrative:
            st.write(narrative)
        else:
            st.info(
                "Narrative unavailable (LLM disabled or rate limited). "
                "The charts and metrics above provide the full historical picture."
            )

    except Exception as e:
        st.error(f"Analysis failed: {e}")
