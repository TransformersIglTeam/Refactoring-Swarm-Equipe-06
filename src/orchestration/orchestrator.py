"""
Main orchestrator for the multi-agent refactoring system.
"""

import logging
import sys
from typing import Optional

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


class OrchestratorConfig:
    """Configuration for the Orchestrator."""
    
    DEFAULT_MAX_ITERATIONS = 10
    
    def __init__(
        self,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ):
        self.max_iterations = max_iterations


class Orchestrator:
    """
    Main orchestrator for the multi-agent fix process.
    
    This class manages the workflow execution and state initialization.
    """
    
    def __init__(
        self,
        project_path: str,
        error_context: str = "",
        config: Optional[OrchestratorConfig] = None
    ):
        """
        Initialize the orchestrator.
        
        Args:
            project_path: Path to the project to fix.
            error_context: Optional initial error context.
            config: Optional configuration object.
        """
        self.config = config or OrchestratorConfig()
        self.initial_state = self._create_initial_state(project_path, error_context)
        self.app = create_workflow()
    
    def _create_initial_state(self, project_path: str, error_context: str) -> dict:
        """Create the initial state for the workflow."""
        return {
            "project_path": project_path,
            "error_context": error_context,
            "current_iteration": 0,
            "max_iterations": self.config.max_iterations,
            "analysis_result": None,
            "proposed_fixes": [],
            "judge_feedback": None,
            "is_fixed": False,
            "audit_report": None,
            "audit_passed": False,
            "history": [],
            "tests_found": False,
            "tests_passed": False,
            "generate_tests_prompt": ""
        }

    def start(self) -> AgentState:
        """
        Start the multi-agent fix process.
        
        Returns:
            Final state after workflow completion.
        """
        logger.info(f"Starting orchestration for project: {self.initial_state['project_path']}")
        
        final_state = self.app.invoke(self.initial_state)
        
        self._log_completion_summary(final_state)
        
        return final_state
    
    def _log_completion_summary(self, final_state: dict):
        """Log a summary of the orchestration completion."""
        logger.info("=" * 50)
        logger.info("Orchestration finished.")
        logger.info(f"  Tests found: {final_state.get('tests_found', False)}")
        logger.info(f"  Tests passed: {final_state.get('tests_passed', False)}")
        logger.info(f"  Is fixed: {final_state.get('is_fixed', False)}")
        logger.info(f"  Iterations: {final_state.get('current_iteration', 0)}")
        logger.info("=" * 50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.orchestration.orchestrator <project_path> [error_context]")
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
