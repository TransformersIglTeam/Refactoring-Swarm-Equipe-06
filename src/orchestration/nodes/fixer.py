"""
Fixer node for the orchestration workflow.
"""

import logging
from src.orchestration.state import AgentState
from src.orchestration.agents import get_fixer_agent

logger = logging.getLogger(__name__)


def node_fixer(state: AgentState) -> dict:
    """
    Fixer node that applies fixes to the project.
    
    Args:
        state: Current agent state.
        
    Returns:
        Updated state fields.
    """
    logger.info("--- FIXER NODE ---")
    
    current_iter = state["current_iteration"] + 1
    fixer_agent = get_fixer_agent()
    
    if not fixer_agent:
        logger.warning("Fixer agent not found.")
        return {
            "current_iteration": current_iter,
            "proposed_fixes": ["N/A - Agent missing"]
        }
    
    # Get context for fixing
    analysis = state.get("analysis_result", "")
    feedback = state.get("judge_feedback", "")
    
    # Apply fixes
    fixes = fixer_agent.fix(state["project_path"], analysis, feedback)
    
    return {
        "current_iteration": current_iter,
        "proposed_fixes": [fixes],
        "history": [{
            "agent": "Fixer",
            "action": "fix",
            "result": fixes,
            "iteration": current_iter
        }]
    }
