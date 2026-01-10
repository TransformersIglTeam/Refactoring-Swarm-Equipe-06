"""
Agent management and initialization for the orchestration pipeline.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-loaded agent instances
_auditor_agent = None
_fixer_agent = None
_judge_agent = None
_agents_initialized = False


def _initialize_agents():
    """Initialize all agents. Called once on first access."""
    global _auditor_agent, _fixer_agent, _judge_agent, _agents_initialized
    
    if _agents_initialized:
        return
    
    # Import agents
    try:
        from src.agents.auditor.AuditorAgent import AuditorAgent
        _auditor_agent = AuditorAgent()
        logger.info("AuditorAgent initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize AuditorAgent: {e}")
        _auditor_agent = None
    
    try:
        from src.agents.fixer.FixerAgent import FixerAgent
        _fixer_agent = FixerAgent()
        logger.info("FixerAgent initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize FixerAgent: {e}")
        _fixer_agent = None
    
    try:
        from src.agents.judge.JudgeAgent import JudgeAgent
        _judge_agent = JudgeAgent()
        logger.info("JudgeAgent initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize JudgeAgent: {e}")
        _judge_agent = None
    
    _agents_initialized = True


def get_auditor_agent() -> Optional[object]:
    """Get the auditor agent instance."""
    _initialize_agents()
    return _auditor_agent


def get_fixer_agent() -> Optional[object]:
    """Get the fixer agent instance."""
    _initialize_agents()
    return _fixer_agent


def get_judge_agent() -> Optional[object]:
    """Get the judge agent instance."""
    _initialize_agents()
    return _judge_agent


def reset_agents():
    """Reset all agents. Useful for testing."""
    global _auditor_agent, _fixer_agent, _judge_agent, _agents_initialized
    _auditor_agent = None
    _fixer_agent = None
    _judge_agent = None
    _agents_initialized = False
