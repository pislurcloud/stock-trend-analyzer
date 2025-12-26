from llm.client import LLMClient
from llm.state import AnalysisState


def trend_explanation_agent(state: AnalysisState) -> dict:
    llm = LLMClient(
        models=[
            "meta-llama/llama-3.3-70b-instruct:free",
            "deepseek/deepseek-r1-0528:free",
            "gpt-4o-mini",
        ]
    )

    user_prompt = f"""
Explain why the stock is classified as {state['dominant_trend']}.

Use the following evidence:
- CAGR over the analysis period: {state['cagr']}%
- Price multiple over the period: {state['price_multiple']}x
- Trend distribution: {state['trend_distribution']}
- Recent trend behavior: {state['recent_trend']}

If the stock shows strong long-term returns despite consolidation phases,
explicitly explain this nuance.

Avoid speculation or future-oriented language.

DATA:
{state}
"""

    output = llm.generate(
        system_prompt="You explain historical trend behavior using evidence only.",
        user_prompt=user_prompt,
    )

    return {"trend_explanation": output}
