import streamlit as st

from core.analytics_pipeline import run_trend_analysis
from llm.narrative import generate_narrative


st.set_page_config(page_title="Stock Performance Snapshot", layout="wide")

st.title("📈 Stock Performance Snapshot")
st.caption(
    "Historical performance analysis based on adjusted price data only. "
    "This tool is informational and does not provide investment advice."
)

with st.sidebar:
    st.header("Analysis Settings")
    ticker = st.text_input("Stock Ticker", value="AAPL")
    years = st.slider("Lookback Period (Years)", 5, 15, 10)
    run_button = st.button("Run Analysis")

if run_button:
    try:
        snapshot = run_trend_analysis(ticker.strip().upper(), years)

        # -------------------------------------------------
        # Executive Snapshot
        # -------------------------------------------------
        st.subheader("📊 Executive Snapshot")
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("CAGR", f"{snapshot['growth']['cagr']}%")
        c2.metric("Total Return", f"{snapshot['growth']['total_return_pct']}%")
        c3.metric("Max Drawdown", f"{snapshot['risk']['max_drawdown']}%")
        c4.metric("Volatility", f"{snapshot['consistency']['annualized_volatility']}%")

        # -------------------------------------------------
        # Charts
        # -------------------------------------------------
        st.subheader("📈 Price Performance")
        st.line_chart(snapshot["charts"]["price"].set_index("date"))

        st.subheader("📉 Drawdowns")
        st.area_chart(snapshot["charts"]["drawdown"].set_index("date"))

        st.subheader("🔄 Rolling 12-Month Returns")
        st.line_chart(snapshot["charts"]["rolling_12m"].set_index("date"))

        # -------------------------------------------------
        # Benchmark Comparison
        # -------------------------------------------------
        st.subheader("📊 Benchmark Comparison")

        bench = snapshot["benchmark"]

        b1, b2, b3 = st.columns(3)
        b1.metric(
            "Stock CAGR vs Benchmark",
            f"{snapshot['growth']['cagr']}% vs {bench['cagr']}%",
        )
        b2.metric(
            "Volatility vs Benchmark",
            f"{snapshot['consistency']['annualized_volatility']}% vs {bench['annualized_volatility']}%",
        )
        b3.metric(
            "Drawdown vs Benchmark",
            f"{snapshot['risk']['max_drawdown']}% vs {bench['max_drawdown']}%",
        )

        if snapshot["summary_flags"]["outperformed_benchmark"]:
            st.success("The stock outperformed the benchmark on a CAGR basis.")
        else:
            st.info("The stock underperformed the benchmark on a CAGR basis.")

        # -------------------------------------------------
        # Narrative
        # -------------------------------------------------
        st.subheader("📝 Investor Narrative")

        with st.spinner("Generating narrative summary..."):
            narrative = generate_narrative(snapshot)

        if narrative:
            st.write(narrative)
        else:
            st.info("Narrative unavailable. Metrics above provide full context.")

    except Exception as e:
        st.error(f"Analysis failed: {e}")
