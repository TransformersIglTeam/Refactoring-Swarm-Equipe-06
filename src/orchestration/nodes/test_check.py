"""
Test check middleware node for the orchestration workflow.
"""

import logging
from src.orchestration.state import AgentState
from src.orchestration.middleware.test_discovery import TestDiscovery
from src.orchestration.middleware.test_runner import TestRunner
from src.orchestration.middleware.prompts import TestPrompts

logger = logging.getLogger(__name__)


def node_test_check(state: AgentState) -> dict:
    """
    Middleware to check if unit tests exist and if they pass.
    
    This node runs before the agent loop to determine if fixes are needed.
    
    Args:
        state: Current agent state.
        
    Returns:
        Updated state fields.
    """
    logger.info("--- TEST CHECK MIDDLEWARE (Unit Tests) ---")
    
    project_path = state["project_path"]
    
    # Discover tests
    discovery = TestDiscovery(project_path)
    discovery_result = discovery.discover()
    
    if not discovery_result.tests_found:
        return _handle_no_tests_found()
    
    # Run tests
    logger.info(f"Unit tests found in: {discovery_result.test_directory}. Running tests...")
    
    runner = TestRunner(project_path)
    run_result = runner.run(discovery_result.test_directory)
    
    return _handle_test_result(run_result)


def _handle_no_tests_found() -> dict:
    """Handle the case when no tests are found."""
    logger.info("No unit tests found in the project.")
    
    return {
        "tests_found": False,
        "tests_passed": False,
        "is_fixed": False,
        "generate_tests_prompt": TestPrompts.get_no_tests_prompt(),
        "history": [{
            "agent": "TestCheck",
            "action": "check_unit_tests",
            "result": "No unit tests found",
            "iteration": 0
        }]
    }


def _handle_test_result(run_result) -> dict:
    """Handle the test run result."""
    if run_result.success:
        logger.info("✅ All unit tests passed! Project is healthy - skipping all agents.")
    else:
        logger.info("Unit tests found but some failed.")
        if run_result.output:
            logger.info(f"Test output:\n{run_result.output[:1000]}")
    
    return {
        "tests_found": True,
        "tests_passed": run_result.success,
        "is_fixed": run_result.success,
        "generate_tests_prompt": "",
        "error_context": run_result.output if not run_result.success else "",
        "history": [{
            "agent": "TestCheck",
            "action": "run_unit_tests",
            "result": run_result.output[:1000] if run_result.output else run_result.error or "",
            "iteration": 0
        }]
    }
