"""
Init files for clean module structure
"""

# ============================================
# src/agents/judge/__init__.py
# ============================================
from .JudgeAgent import JudgeAgent
from .Models import (
    JudgeResult,
    TestResult,
    JudgeDecision,
    TestStatus,
    FailureDetail
)

__all__ = [
    'JudgeAgent',
    'JudgeResult',
    'TestResult',
    'JudgeDecision',
    'TestStatus',
    'FailureDetail'
]



# ============================================
# src/tools/testing/__init__.py
# ============================================
