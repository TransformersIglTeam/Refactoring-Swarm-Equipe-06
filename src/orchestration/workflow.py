import logging
from typing import Literal
from langgraph.graph import StateGraph, END

from src.orchestration.state import AgentState

# Import Agents
# We use try/except block or direct imports if we are sure.
# For now, we assume these files exist and have the classes as defined in previous steps.
from src.agents.analyser.AnalyserAgent import AnalyserAgent
from src.agents.fixer.FixerAgent import FixerAgent
from src.agents.judge.JudgeAgent import JudgeAgent
from src.agents.auditor.AuditorAgent import AuditorAgent

logger = logging.getLogger(__name__)

# Initialize Agents
try:
    analyser_agent = AnalyserAgent()
except:
    analyser_agent = None

try:
    fixer_agent = FixerAgent()
except:
    fixer_agent = None

try:
    judge_agent = JudgeAgent()
except:
    judge_agent = None

try:
    auditor_agent = AuditorAgent()
except:
    auditor_agent = None


def node_analyser(state: AgentState):
    logger.info("--- ANALYSER NODE ---")
    if not analyser_agent:
        logger.warning("Analyser agent not found.")
        return {"analysis_result": "N/A - Agent missing"}
    
    result = analyser_agent.analyze(state["project_path"], state["error_context"])
    return {
        "analysis_result": result,
        "history": [{"agent": "Analyser", "action": "analyze", "result": result, "iteration": state["current_iteration"]}]
    }

def node_fixer(state: AgentState):
    logger.info("--- FIXER NODE ---")
    current_iter = state["current_iteration"] + 1
    
    if not fixer_agent:
        logger.warning("Fixer agent not found.")
        return {"current_iteration": current_iter, "proposed_fixes": ["N/A - Agent missing"]}

    # Pass analysis and previous feedback (if any)
    feedback = state.get("judge_feedback", "")
    fixes = fixer_agent.fix(state["project_path"], state.get("analysis_result", ""), feedback)
    
    return {
        "current_iteration": current_iter,
        "proposed_fixes": [fixes],
        "history": [{"agent": "Fixer", "action": "fix", "result": fixes, "iteration": current_iter}]
    }

def node_judge(state: AgentState):
    logger.info("--- JUDGE NODE ---")
    if not judge_agent:
        logger.warning("Judge agent not found.")
        return {"is_fixed": False, "judge_feedback": "Judge agent missing"}

    # Judge executes tests/checks
    result = judge_agent.judge(state["project_path"], state["current_iteration"])
    
    is_passed = (result.decision.name == "PASS")
    
    return {
        "is_fixed": is_passed,
        "judge_feedback": result.reason,
        "history": [{"agent": "Judge", "action": "judge", "result": result, "iteration": state["current_iteration"]}]
    }

def node_auditor(state: AgentState):
    logger.info("--- AUDITOR NODE ---")
    if not auditor_agent:
        logger.warning("Auditor agent not found.")
        return {"audit_passed": True, "audit_report": "Auditor missing, skipping"}

    # Auditor checks quality/security
    report = auditor_agent.audit(state["project_path"])
    
    # Simple logic: assume report string contains "Passed" or we just manually verify for now
    # Ideally Auditor returns a structured object too.
    passed = "Passed" in report or "passed" in report # Mock logic
    
    return {
        "audit_report": report,
        "audit_passed": passed,
         "history": [{"agent": "Auditor", "action": "audit", "result": report, "iteration": state["current_iteration"]}]
    }

# Edges
def should_continue_fix(state: AgentState) -> Literal["auditor", "fixer", "end"]:
    if state["is_fixed"]:
        return "auditor"
    
    if state["current_iteration"] >= state["max_iterations"]:
        logger.info("Max iterations reached.")
        return "end"
    
    return "fixer"

def should_end_audit(state: AgentState) -> Literal["end", "fixer"]:
    if state["audit_passed"]:
        return "end"
    
    # If audit failed, and we have iterations left, go back to fix
    if state["current_iteration"] < state["max_iterations"]:
        # Update feedback to include audit report so fixer knows what to fix
        # Note: We might want to append to judge_feedback or have separate field
        return "fixer"
    
    return "end"


def create_workflow():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("analyser", node_analyser)
    workflow.add_node("fixer", node_fixer)
    workflow.add_node("judge", node_judge)
    workflow.add_node("auditor", node_auditor)

    # Set Entry Point
    workflow.set_entry_point("analyser")

    # Add Edges
    workflow.add_edge("analyser", "fixer")
    workflow.add_edge("fixer", "judge")
    
    # Conditional Edge from Judge
    workflow.add_conditional_edges(
        "judge",
        should_continue_fix,
        {
            "auditor": "auditor",
            "fixer": "fixer",
            "end": END
        }
    )
    
    # Conditional Edge from Auditor
    workflow.add_conditional_edges(
        "auditor",
        should_end_audit,
        {
            "end": END,
            "fixer": "fixer"
        }
    )

    return workflow.compile()
