import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    parser.add_argument("--run-agent", action="store_true", help="Run the JudgeAgent against the target_dir")
    args = parser.parse_args()

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE SUR : {args.target_dir}")
    # Log startup
    try:
        log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")
    except Exception:
        # non-fatal if logger isn't configured in this environment
        pass

    # Check API key is available (loaded from .env)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found in environment. Agent requests will fail without it.")

    # Optionally run the JudgeAgent against the target directory for a quick integration smoke test
    if args.run_agent:
        try:
            from src.utils.SandboxSetup import setup_project_sandbox
            from src.agents.judge.JudgeAgent import JudgeAgent

            setup_project_sandbox(args.target_dir)
            judge = JudgeAgent()
            print("\n🔎 Running JudgeAgent smoke test...\n")
            result = judge.judge_and_print(args.target_dir)
            print("\n✅ JudgeAgent finished.\n")
        except Exception as e:
            print(f"❌ Agent run failed: {e}")
    print("✅ MISSION_COMPLETE")

if __name__ == "__main__":
    main()