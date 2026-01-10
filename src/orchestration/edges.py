"""
Workflow edge functions for conditional routing.
"""

import logging
from typing import Literal
from src.orchestration.state import AgentState

logger = logging.getLogger(__name__)


def should_enter_loop(state: AgentState) -> Literal["auditor", "end"]:
    """
    Decide whether to enter the agent loop after test check.
    
    Args:
        state: Current agent state.
        
    Returns:
        Next node: "auditor" to enter loop, "end" to exit.
    """
    if state.get("tests_passed", False):
        logger.info("✅ All tests passing. No agents will be run - project is healthy!")
        return "end"
    
    logger.info("Tests failed or not found. Entering agent fix loop...")
    return "auditor"


def should_continue_fix(state: AgentState) -> Literal["auditor", "end"]:
    """
    Decide whether to continue the fix loop or exit.
    
    Args:
        state: Current agent state.
        
    Returns:
        Next node: "auditor" to continue, "end" to exit.
    """
    if state["is_fixed"]:
        logger.info("✅ Project is fixed! Exiting.")
        return "end"
    
    if state["current_iteration"] >= state["max_iterations"]:
        logger.info(f"Max iterations ({state['max_iterations']}) reached. Exiting.")
        return "end"
    
    logger.info(
        f"Project not fixed yet. "
        f"Iteration {state['current_iteration']}/{state['max_iterations']}. "
        f"Continuing..."
    )
    return "auditor"
