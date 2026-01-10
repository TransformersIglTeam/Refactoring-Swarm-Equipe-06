"""
Workflow definition for the multi-agent orchestration pipeline.
"""

import logging
from langgraph.graph import StateGraph, END

from src.orchestration.state import AgentState
from src.orchestration.nodes import (
    node_test_check,
    node_auditor,
    node_fixer,
    node_judge
)
from src.orchestration.edges import should_enter_loop, should_continue_fix

logger = logging.getLogger(__name__)


def create_workflow():
    """
    Create and compile the orchestration workflow.
    
    The workflow follows this pattern:
    1. Test Check (middleware) - Run tests first
    2. If tests pass -> End (no fixes needed)
    3. If tests fail -> Auditor -> Fixer -> Judge
    4. If Judge passes -> End
    5. If Judge fails and iterations remain -> Back to Auditor
    6. If max iterations reached -> End
    
    Returns:
        Compiled LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("test_check", node_test_check)
    workflow.add_node("auditor", node_auditor)
    workflow.add_node("fixer", node_fixer)
    workflow.add_node("judge", node_judge)

    # Set entry point
    workflow.set_entry_point("test_check")

    # Add edges
    # Test Check -> Conditional (Auditor or End)
    workflow.add_conditional_edges(
        "test_check",
        should_enter_loop,
        {
            "auditor": "auditor",
            "end": END
        }
    )
    
    # Auditor -> Fixer
    workflow.add_edge("auditor", "fixer")
    
    # Fixer -> Judge
    workflow.add_edge("fixer", "judge")
    
    # Judge -> Conditional (Auditor or End)
    workflow.add_conditional_edges(
        "judge",
        should_continue_fix,
        {
            "auditor": "auditor",
            "end": END
        }
    )

    logger.debug("Workflow compiled successfully")
    return workflow.compile()

