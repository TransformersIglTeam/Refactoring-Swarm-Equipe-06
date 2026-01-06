from typing import List, Optional, Dict, Any, TypedDict, Annotated
import operator

def add_item(current: List, new: List) -> List:
    if not current:
        return new
    return current + new

class AgentState(TypedDict):
    """
    Shared state for the multi-agent system.
    Tracks the progress of fixing a codebase.
    """
    project_path: str
    error_context: str
    current_iteration: int
    max_iterations: int
    
    # Analysis
    analysis_result: Optional[str]
    
    # Fix
    proposed_fixes: Annotated[List[str], add_item]
    
    # Verification (Judge)
    judge_feedback: Optional[str]
    is_fixed: bool
    
    # Audit
    audit_report: Optional[str]
    audit_passed: bool
    
    # History
    history: Annotated[List[Dict[str, Any]], add_item]
