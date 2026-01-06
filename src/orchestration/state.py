from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """
    Shared state for the multi-agent system.
    Tracks the progress of fixing a codebase.
    """
    project_path: str = Field(description="Path to the project being fixed")
    error_context: str = Field(description="Initial error report or traceback")
    current_iteration: int = Field(default=0, description="Current fix attempt iteration")
    max_iterations: int = Field(default=5, description="Maximum number of fix attempts")
    
    # Analysis
    analysis_result: Optional[str] = Field(default=None, description="Root cause analysis from Analyzer")
    
    # Fix
    proposed_fixes: List[str] = Field(default_factory=list, description="List of proposed code changes/diffs")
    
    # Verification (Judge)
    judge_feedback: Optional[str] = Field(default=None, description="Feedback from the Judge")
    is_fixed: bool = Field(default=False, description="Whether the issue is resolved")
    
    # Audit
    audit_report: Optional[str] = Field(default=None, description="Security and style audit report")
    audit_passed: bool = Field(default=False, description="Whether the audit passed")
    
    # History
    history: List[Dict[str, Any]] = Field(default_factory=list, description="Log of actions taken")

    def add_history(self, agent_name: str, action: str, result: Any):
        self.history.append({
            "agent": agent_name,
            "action": action,
            "result": result,
            "iteration": self.current_iteration
        })
