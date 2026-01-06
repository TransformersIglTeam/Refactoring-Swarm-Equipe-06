import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.utils.SandboxSetup import setup_project_sandbox
from src.agents.auditor.AuditorAgent import AuditorAgent

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, help="Path to the project to audit")
    args = parser.parse_args()

    if not args.target_dir:
        # Default to test_project if not specified
        args.target_dir = os.path.abspath("test_project")

    if not os.path.exists(args.target_dir):
        print(f"❌ Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f"🚀 DEMARRAGE AUDITOR AGENT SUR : {args.target_dir}")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("⚠️  GOOGLE_API_KEY not found in environment. Agent requests will fail.")

    try:
        # 1. Setup Sandbox
        setup_project_sandbox(args.target_dir)

        # 2. Initialize Auditor Agent
        auditor = AuditorAgent()
        
        # 3. Run Auditor
        print("🕵️  Running AuditorAgent...")
        result = auditor.audit(
            project_path=args.target_dir
        )
        
        print("\n✅ Auditor Output:")
        print(result)
        
    except Exception as e:
        print(f"❌ Auditor run failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()