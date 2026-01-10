"""
Auditor node for the orchestration workflow.
"""

import logging
from src.orchestration.state import AgentState
from src.orchestration.agents import get_auditor_agent

logger = logging.getLogger(__name__)


def node_auditor(state: AgentState) -> dict:
    """
    Auditor node that analyzes the project for issues.
    
    Args:
        state: Current agent state.
        
    Returns:
        Updated state fields.
    """
    logger.info("--- AUDITOR NODE ---")
    
    auditor_agent = get_auditor_agent()
    
    if not auditor_agent:
        logger.warning("Auditor agent not found.")
        return {
            "audit_passed": True,
            "audit_report": "Auditor missing, skipping"
        }
    
    # Get the dynamic prompt for test generation (if any)
    additional_context = state.get("generate_tests_prompt", "")
    
    # Run the audit
    report = auditor_agent.audit(state["project_path"])
    
    # Prepend test generation instructions if needed
    if additional_context:
        report = f"{additional_context}\n\n{report}"
    
    # Determine if audit passed (simple heuristic)
    passed = _check_audit_passed(report)
    
    return {
        "audit_report": report,
        "audit_passed": passed,
        "analysis_result": report,
        "history": [{
            "agent": "Auditor",
            "action": "audit",
            "result": report,
            "iteration": state["current_iteration"]
        }]
    }


def _check_audit_passed(report: str) -> bool:
    """Check if the audit passed based on the report content."""
    report_lower = report.lower()
    return "passed" in report_lower or "no issues" in report_lower
