from llm.client import LLMClient
from llm.state import AnalysisState


def final_narrative_agent(state: AnalysisState) -> dict:
    #llm = LLMClient(model="openai/gpt-4o-mini")
    llm = LLMClient(
    models=[
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528:free",
        "gpt-4o-mini",
    ]
    )


    user_prompt = f"""
Combine the following sections into a single investor-friendly narrative.
Ensure consistency in tone and confidence.
End with a reminder that this analysis is historical and informational only.

EXECUTIVE SUMMARY:
{state['exec_summary']}

TREND EXPLANATION:
{state['trend_explanation']}

RISKS & RED FLAGS:
{state['risk_analysis']}

BENCHMARK COMPARISON:
{state['benchmark_analysis']}
"""

    output = llm.generate(
        system_prompt="You generate neutral, investor-facing summaries.",
        user_prompt=user_prompt
    )

    return {"final_narrative": output}
