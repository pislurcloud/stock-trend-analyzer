import logging
from llm.client import LLMClient

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
from openai import OpenAI

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()


# -------------------------------------------------
# Model preference order (free first)
# -------------------------------------------------
OPENROUTER_FREE_MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "deepseek/deepseek-r1-0528:free",
    "tngtech/deepseek-r1t2-chimera:free",
]

OPENAI_FALLBACK_MODELS = [
    "gpt-3.5-turbo",
]


def generate_narrative(snapshot: dict) -> str | None:
    """
    Generate an investor-friendly narrative from the performance snapshot.
    Works with the current analytics schema (no trend_context dependency).
    """

    try:
        llm = LLMClient()

        meta = snapshot["meta"]
        growth = snapshot["growth"]
        risk = snapshot["risk"]
        consistency = snapshot["consistency"]
        benchmark = snapshot["benchmark"]
        flags = snapshot["summary_flags"]

        system_prompt = (
            "You are a financial analyst explaining historical stock performance "
            "Write in natural, conversational English."
            "Avoid repeating phrases or statistics."
            "Explain what it felt like to hold the stock over time."
            "Frame sideways periods as pauses or consolidation if long-term growth was strong."
            "Do not sound mechanical or repetitive."
            "Do not overemphasize sideways percentages."
            "Explain sideways movement as consolidation or pauses if long-term growth was strong."
            "Do not give investment advice or predict future performance."
        )

        user_prompt = f"""
Stock analyzed: {meta['ticker']}
Benchmark used: {meta['benchmark']}

Key historical facts:
- Average annual growth (CAGR): {growth['cagr']}%
- Total price increase over period: {growth['total_return_pct']}%
- Largest historical drawdown: {risk['max_drawdown']}%
- Annualized volatility: {consistency['annualized_volatility']}%

Benchmark comparison:
- Stock CAGR: {growth['cagr']}%
- Benchmark CAGR: {benchmark['cagr']}%
- Stock volatility: {consistency['annualized_volatility']}%
- Benchmark volatility: {benchmark['annualized_volatility']}%

Flags:
- Strong long-term compounder: {flags['outperformed_benchmark']}
- Higher volatility than benchmark: {flags['higher_volatility_than_benchmark']}

Write a short, clear paragraph explaining:
1) How the stock grew over time
2) The kind of ups and downs an investor experienced
3) Whether it outperformed the broader market
4) What type of investor temperament this stock historically suited

End with:
"This is historical analysis only and not investment advice."
"""

        response = llm.generate(system_prompt, user_prompt)
        return response


        
    except Exception as e:
        logger.warning(f"LLM narrative failed: {e}")
        return None
