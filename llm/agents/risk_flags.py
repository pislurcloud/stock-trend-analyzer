from llm.client import LLMClient
from llm.state import AnalysisState


def risk_flags_agent(state: AnalysisState) -> dict:
    #llm = LLMClient(model="meta-llama/llama-3-8b-instruct")
    llm = LLMClient(
    models=[
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528:free",
    ]
    )


    user_prompt = f"""
Summarize the key historical risks and red flags.
Explain why they matter historically.
Do not exaggerate risk or predict losses.

DATA:
{state}
"""

    output = llm.generate(
        system_prompt="You explain historical risks conservatively.",
        user_prompt=user_prompt
    )

    return {"risk_analysis": output}
