"""
Judge node for the orchestration workflow.
"""

import logging
from src.orchestration.state import AgentState
from src.orchestration.agents import get_judge_agent

logger = logging.getLogger(__name__)


def node_judge(state: AgentState) -> dict:
    """
    Judge node that evaluates if fixes were successful.
    
    Args:
        state: Current agent state.
        
    Returns:
        Updated state fields.
    """
    logger.info("--- JUDGE NODE ---")
    
    judge_agent = get_judge_agent()
    
    if not judge_agent:
        logger.warning("Judge agent not found.")
        return {
            "is_fixed": False,
            "judge_feedback": "Judge agent missing"
        }
    
    # Evaluate the fixes
    result = judge_agent.judge(state["project_path"], state["current_iteration"])
    
    is_passed = (result.decision.name == "PASS")
    
    return {
        "is_fixed": is_passed,
        "judge_feedback": result.reason,
        "history": [{
            "agent": "Judge",
            "action": "judge",
            "result": str(result),
            "iteration": state["current_iteration"]
        }]
    }
