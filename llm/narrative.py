import os
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


# -------------------------------------------------
# Narrative generator
# -------------------------------------------------
def generate_narrative(snapshot: dict) -> str | None:
    """
    Generate a layman-friendly investor / trader narrative
    from a historical performance snapshot.

    - Uses simple, non-technical language
    - Explains what the investor experienced
    - No predictions or advice
    - Falls back gracefully if LLMs fail
    """

    # -----------------------------
    # Extract snapshot sections
    # -----------------------------
    g = snapshot["growth"]
    r = snapshot["risk"]
    c = snapshot["consistency"]
    t = snapshot["trend_context"]
    flags = snapshot["summary_flags"]

    # -----------------------------
    # Layman-friendly prompt
    # -----------------------------
    system_prompt = (
        "You are explaining stock performance to a layman investor or trader."
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
Below is a 10-year historical performance summary of a stock, based only on price data.

Explain it in plain English so that a non-technical investor can easily understand it.

Growth:
- Average yearly growth: {g['cagr']}%
- Price increase multiple: {g['price_multiple']}x
- Total price increase: {g['total_return_pct']}%
- Positive years: {int(g['positive_year_ratio'] * 100)}% of years

Risk and declines:
- Largest fall from peak: {r['max_drawdown']}%
- Worst one-year period: {r['worst_rolling_12m']}%

Stability:
- Price volatility: {c['annualized_volatility']}%
- Risk-adjusted return score: {c['sharpe_like']}

Price behaviour:
- How often it moved up, sideways, or down: {t['regime_distribution']}
- Most recent behaviour: {t['recent_regime']}

Additional observations:
{flags}

Write a short narrative (120–150 words) that covers:
1) How well the stock grew overall
2) How rough or smooth the journey was
3) Whether gains came steadily or in bursts
4) How sideways phases fit into the bigger picture

End clearly by stating that this is historical analysis only and not investment advice.
"""

    # -------------------------------------------------
    # Try OpenRouter free models first
    # -------------------------------------------------
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if openrouter_key:
        client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1",
        )

        for model in OPENROUTER_FREE_MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.4,
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"[OpenRouter] Model failed: {model} | {e}")

    # -------------------------------------------------
    # Fallback to OpenAI (if quota exists)
    # -------------------------------------------------
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        client = OpenAI(api_key=openai_key)

        for model in OPENAI_FALLBACK_MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.4,
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                print(f"[OpenAI] Model failed: {model} | {e}")

    # -------------------------------------------------
    # All models failed
    # -------------------------------------------------
    return None
