"""
State definitions for the multi-agent orchestration system.
"""

from typing import List, Optional, Dict, Any, TypedDict, Annotated


def merge_lists(current: List, new: List) -> List:
    """Merge two lists, handling None values."""
    if not current:
        return new or []
    if not new:
        return current
    return current + new


class AgentState(TypedDict):
    """
    Shared state for the multi-agent system.
    
    This state is passed between all nodes in the workflow and
    tracks the progress of fixing a codebase.
    
    Attributes:
        project_path: Path to the project being fixed.
        error_context: Initial error context or test output.
        current_iteration: Current iteration number.
        max_iterations: Maximum allowed iterations.
        analysis_result: Result from the auditor analysis.
        proposed_fixes: List of fixes proposed by the fixer.
        judge_feedback: Feedback from the judge.
        is_fixed: Whether the project is fixed.
        audit_report: Full audit report.
        audit_passed: Whether the audit passed.
        history: History of all agent actions.
        tests_found: Whether tests were found.
        tests_passed: Whether tests passed.
        generate_tests_prompt: Dynamic prompt for test generation.
    """
    # Project info
    project_path: str
    error_context: str
    
    # Iteration tracking
    current_iteration: int
    max_iterations: int
    
    # Analysis results
    analysis_result: Optional[str]
    
    # Fix tracking
    proposed_fixes: Annotated[List[str], merge_lists]
    
    # Verification results
    judge_feedback: Optional[str]
    is_fixed: bool
    
    # Audit results
    audit_report: Optional[str]
    audit_passed: bool
    
    # Action history
    history: Annotated[List[Dict[str, Any]], merge_lists]
    
    # Test middleware fields
    tests_found: bool
    tests_passed: bool
    generate_tests_prompt: str
