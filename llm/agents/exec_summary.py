from llm.client import LLMClient
from llm.state import AnalysisState


def exec_summary_agent(state: AnalysisState) -> dict:
    #llm = LLMClient(model="openai/gpt-4o-mini")
    llm = LLMClient(
    models=[
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528:free",
        "gpt-4o-mini",
    ]
    )


    system_prompt = (
        "You are a financial analytics assistant. "
        "Explain historical stock performance only. "
        "Do not provide investment advice or predictions."
    )

    user_prompt = f"""
Write a concise executive summary (4–5 sentences).
State the dominant trend and confidence level.
Mention recent trend if different from long-term trend.

DATA:
{state}
"""

    output = llm.generate(system_prompt, user_prompt)

    return {"exec_summary": output}
