import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.utils.SandboxSetup import setup_project_sandbox


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

        # 2. Define Analysis (Mock or User Provided)
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

        # 3. Initialize and Run Orchestrator
        from src.orchestration.orchestrator import Orchestrator
        
        print("🤖 Initializing Orchestrator Swarm...")
        orchestrator = Orchestrator(project_path=args.target_dir, error_context=analysis_input)
        
        print("▶️  Starting Orchestration Loop...")
        final_state = orchestrator.start()
        
        print("\n🏁 Orchestration Finished.")
        print("Final State Summary:")
        print(f"  Fixed: {final_state.get('is_fixed')}")
        print(f"  Iterations: {final_state.get('current_iteration')}")
        print(f"  Audit Passed: {final_state.get('audit_passed')}")
        
    except Exception as e:
        print(f"❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()