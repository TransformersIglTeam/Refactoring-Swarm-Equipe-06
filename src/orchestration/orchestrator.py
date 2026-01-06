import logging
import sys
from src.orchestration.state import AgentState
from src.orchestration.workflow import create_workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, project_path: str, error_context: str = ""):
        self.initial_state = {
            "project_path": project_path,
            "error_context": error_context,
            "current_iteration": 0,
            "max_iterations": 10,
            "analysis_result": None,
            "proposed_fixes": [],
            "judge_feedback": None,
            "is_fixed": False,
            "audit_report": None,
            "audit_passed": False,
            "history": []
        }
        self.app = create_workflow()

    def start(self) -> AgentState:
        """
        Starts the multi-agent fix process using LangGraph.
        """
        logger.info(f"Starting orchestration for project: {self.initial_state['project_path']}")
        
        # Invoke the graph
        final_state = self.app.invoke(self.initial_state)
        
        logger.info("Orchestration finished.")
        return final_state

if __name__ == "__main__":
    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python src/orchestration/orchestrator.py <project_path> [error_context]")
        sys.exit(1)
    
    project_path = sys.argv[1]
    error_context = sys.argv[2] if len(sys.argv) > 2 else ""
    
    orchestrator = Orchestrator(project_path, error_context)
    try:
        result = orchestrator.start()
        print("Final Result State:", result)
    except Exception as e:
        logger.exception("Orchestration failed")
        sys.exit(1)
