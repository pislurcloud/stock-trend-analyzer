from core.full_pipeline import run_full_analysis

from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    result = run_full_analysis("AAPL", years=10)

    print("\n===== FINAL INVESTOR NARRATIVE =====\n")
    print(result["final_narrative"])
