import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.utils.SandboxSetup import setup_project_sandbox
from src.agents.fixer.FixerAgent import FixerAgent

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, help="Path to the project to fix")
    parser.add_argument("--analysis", type=str, default=None, help="Analysis explanation of the bug (optional)")
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE FIXER AGENT SUR : {args.target_dir}")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found in environment. Agent requests will fail.")

    try:
        # 1. Setup Sandbox
        setup_project_sandbox(args.target_dir)

        # 2. Initialize Fixer Agent
        fixer = FixerAgent()
        
        # 3. Define Analysis (Mock or User Provided)
        analysis_input = args.analysis
        if not analysis_input:
            # Default mock analysis for the known test case if not provided
            print("ℹ️  No analysis provided. Using default mock analysis.")
            analysis_input = (
                "The code fails with a TypeError because it attempts to concatenate an integer "
                "and a string in the 'add_numbers' function. "
                "The fix is to ensure strictly arithmetic addition or proper string conversion if intended. "
                "Given the function name 'add_numbers', arithmetic addition is expected."
            )

        print(f"\n📋 Analysis Context:\n{analysis_input}\n")

        # 4. Run Fixer
        print("�️  Running FixerAgent...")
        result = fixer.fix(
            project_path=args.target_dir,
            analysis_result=analysis_input,
            judge_feedback=""
        )
        
        print("\n✅ Fixer Output:")
        print(result)
        
    except Exception as e:
        print(f"❌ Fixer run failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()