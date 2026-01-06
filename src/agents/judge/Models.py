from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TestStatus(Enum):
    """Test execution status"""
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ERROR = "ERROR"
    NO_TESTS = "NO_TESTS"
    TIMEOUT = "TIMEOUT"


class JudgeDecision(Enum):
    """Judge's decision after analyzing tests"""
    PASS = "PASS"
    RETRY = "RETRY"
    MAX_ITERATIONS = "MAX_ITERATIONS"


@dataclass
class TestResult:
    """
    Result of test execution
    This is the main output object from Judge Agent
    """
    status: TestStatus
    tests_passed: int = 0
    tests_failed: int = 0
    tests_total: int = 0
    success: bool = False
    error_messages: List[str] = field(default_factory=list)
    test_output: str = ""
    execution_time: float = 0.0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "status": self.status.value,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_total": self.tests_total,
            "success": self.success,
            "error_messages": self.error_messages,
            "test_output": self.test_output,
            "execution_time": self.execution_time
        }
    
    def print_summary(self):
        """Print a clean console summary"""
        if self.success:
            print(f"✅ All tests passed! ({self.tests_passed}/{self.tests_total})")
        else:
            print(f"❌ Tests failed: {self.tests_failed}/{self.tests_total} failures")
            if self.error_messages:
                print("\n🔍 Error Summary:")
                for i, error in enumerate(self.error_messages[:3], 1):
                    print(f"   {i}. {error}")


@dataclass
class FailureDetail:
    """Details about a single test failure"""
    
    test_name: str
    error_type: str
    error_message: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None    
    fix_suggestion: Optional[str] = None
    def to_dict(self) -> dict:
        return {
            "test_name": self.test_name,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "fix_suggestion": self.fix_suggestion,
        }


@dataclass
class JudgeResult:
    """
    Complete Judge analysis result
    This is what Judge returns after analyzing test results
    """
    decision: JudgeDecision
    test_result: TestResult
    iteration: int
    reason: str
    failures: List[FailureDetail] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "decision": self.decision.value,
            "test_result": self.test_result.to_dict(),
            "iteration": self.iteration,
            "reason": self.reason,
            "failures": [f.to_dict() for f in self.failures],
            "suggestions": self.suggestions
        }
    
    def print_summary(self):
        """Print clean console output"""
        print("\n" + "="*60)
        print(f"🤖 JUDGE DECISION: {self.decision.value}")
        print("="*60)
        print(f"Iteration: {self.iteration}")
        print(f"Reason: {self.reason}")
        
        self.test_result.print_summary()
        
        if self.failures:
            print(f"\n📋 Detailed Failures ({len(self.failures)}):")
            for i, failure in enumerate(self.failures, 1):
                print(f"\n   {i}. {failure.test_name}")
                print(f"      Type: {failure.error_type}")
                print(f"      Error: {failure.error_message}")
                if failure.fix_suggestion:
                    print(f"      💡 Fix: {failure.fix_suggestion}")
        
        if self.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in self.suggestions[:3]:
                print(f"   • {suggestion}")
        
        print("="*60 + "\n")