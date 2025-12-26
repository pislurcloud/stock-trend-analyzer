from llm.client import LLMClient
from llm.state import AnalysisState


def benchmark_agent(state: AnalysisState) -> dict:
    #llm = LLMClient(model="openai/gpt-4o-mini")
    llm = LLMClient(
    models=[
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528:free",
        "gpt-4o-mini",
    ]
    )


    user_prompt = f"""
Explain how the stock performed relative to its benchmark and sector.
Focus strictly on historical comparison.
Avoid judgement or advice.

DATA:
{state}
"""

    output = llm.generate(
        system_prompt="You compare historical performance neutrally.",
        user_prompt=user_prompt
    )

    return {"benchmark_analysis": output}
