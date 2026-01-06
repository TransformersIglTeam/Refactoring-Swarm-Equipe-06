from typing import Optional
import json

from src.agents.judge.BaseAgent import BaseAgent
from src.agents.judge.Models import (
    TestResult, JudgeResult, JudgeDecision,
    FailureDetail, TestStatus
)

from src.tools.testing.TestParser import TestParser
from src.utils.logger import log_experiment, ActionType


class ResultAnalyzer:
    """Analyzes test results and creates JudgeResult decisions"""
    
    def __init__(
        self,
        agent_name: str = "Judge_Agent",
        model_name: str = "gemini-2.5-flash",
        max_iterations: int = 10
    ):
        self.agent_name = agent_name
        self.model_name = model_name
        self.max_iterations = max_iterations
        self.parser = TestParser()
        # BaseAgent used to generate richer failure details when parser fails
        try:
            self.base_agent = BaseAgent(model_name=self.model_name)
        except Exception:
            self.base_agent = None
    
    def analyze(
        self,
        test_result: TestResult,
        iteration: int = 1
    ) -> JudgeResult:
        """
        Analyze test result and make a decision
        
        Args:
            test_result: Result from test execution
            iteration: Current iteration number
            
        Returns:
            JudgeResult with decision and details
        """
        if test_result.success and test_result.tests_passed > 0:
            return self._create_success_result(test_result, iteration)
        
        return self._create_failure_result(test_result, iteration)
    
    def _create_success_result(
        self,
        test_result: TestResult,
        iteration: int = 1,
    ) -> JudgeResult:
        """Create result for successful tests"""

        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": "Analyze test results - all tests passed",
                "output_response": f"Success! {test_result.tests_passed} tests passed",
                "tests_passed": test_result.tests_passed,
                "iteration": iteration,
            },
            status="SUCCESS"
        )

        return JudgeResult(
            decision=JudgeDecision.PASS,
            test_result=test_result,
            iteration=iteration,
            reason=f"All {test_result.tests_passed} tests passed successfully",
            suggestions=["Code is ready for deployment"]
        )
    
    def _create_failure_result(
        self,
        test_result: TestResult,
        iteration: int
    ) -> JudgeResult:
        """Create result for failed tests"""
        
        failures = self._extract_failure_details(test_result)
        
        suggestions = self._generate_suggestions(test_result, failures)
        
        reason = f"{test_result.tests_failed} test(s) failed"
        if test_result.tests_passed > 0:
            reason += f", {test_result.tests_passed} passed"
        
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Analyze test failures (iteration {iteration})",
                "output_response": f"Found {len(failures)} failures. Recommending retry.",
                "tests_failed": test_result.tests_failed,
                "tests_passed": test_result.tests_passed,
                "iteration": iteration,
                "failure_count": len(failures)
            },
            status="RETRY"
        )
        
        return JudgeResult(
            decision=JudgeDecision.RETRY,
            test_result=test_result,
            iteration=iteration,
            reason=reason,
            failures=failures,
            suggestions=suggestions
        )
    
    def _create_max_iterations_result(
        self,
        test_result: TestResult,
        iteration: int
    ) -> JudgeResult:
        """Create result when max iterations reached"""
        
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Check iteration limit: {iteration}/{self.max_iterations}",
                "output_response": "Maximum iterations reached. Stopping.",
                "iteration": iteration,
                "max_iterations": self.max_iterations
            },
            status="MAX_ITERATIONS"
        )
        
        return JudgeResult(
            decision=JudgeDecision.MAX_ITERATIONS,
            test_result=test_result,
            iteration=iteration,
            reason=f"Maximum iterations ({self.max_iterations}) reached without success",
            suggestions=["Manual intervention required", "Review error logs for persistent issues"]
        )
    
    def _extract_failure_details(self, test_result: TestResult) -> list:
        """Extract detailed failure information"""
        failures = []
        
        # Parse detailed failures from output
        detailed = self.parser.extract_failure_details(test_result.test_output)
        
        for detail in detailed:
            failure = FailureDetail(
                test_name=detail.get('test_name', 'Unknown'),
                error_type=detail.get('error_type', 'Unknown'),
                error_message=detail.get('error_message', 'No details available'),
                fix_suggestion=self._suggest_fix(detail.get('error_type', ''))
            )
            failures.append(failure)
        
        # If no detailed failures, create from error messages
        if not failures and test_result.error_messages:
            # Try to ask the LLM (Gemini) to synthesize structured failure details
            generated = None
            if self.base_agent:
                prompt = (
                    "You are a helpful automated test failure analyzer. "
                    "Given the following test error messages and an optional test output excerpt, "
                    "return a JSON array of objects each with the keys: test_name, error_type, error_message, fix_suggestion. "
                    "If a field is unknown, set it to an empty string. Keep the output as pure JSON only.\n\n"
                    f"ERROR_MESSAGES:\n{json.dumps(test_result.error_messages[:5])}\n\n"
                    f"OUTPUT_EXCERPT:\n{test_result.test_output[:1000]}\n\n"
                    "Return only JSON."
                )

                try:
                    response = self.base_agent.llm_call(prompt)
                    # Log LLM interaction
                    try:
                        log_experiment(
                            agent_name="self.agent_name",
                            model_used=self.model_name,
                            action=ActionType.ANALYSIS,
                            details={
                                "input_prompt": prompt,
                                "output_response": response or "",
                            },
                            status="SUCCESS" if response else "NO_RESPONSE"
                        )
                    except Exception:
                        # Don't fail analysis if logging fails
                        pass

                    if response:
                        # Try to parse JSON strictly
                        try:
                            parsed = json.loads(response)
                            if isinstance(parsed, list):
                                generated = parsed
                        except Exception:
                            # fallback: try to extract a JSON substring
                            try:
                                start = response.index("[")
                                end = response.rindex("]") + 1
                                snippet = response[start:end]
                                parsed = json.loads(snippet)
                                if isinstance(parsed, list):
                                    generated = parsed
                            except Exception:
                                generated = None
                except Exception:
                    generated = None

            if generated:
                for item in generated:
                    failure = FailureDetail(
                        test_name=item.get('test_name', 'Unknown') or 'Unknown',
                        error_type=item.get('error_type', 'Unknown') or 'Unknown',
                        error_message=item.get('error_message', 'No details available') or 'No details available',
                        fix_suggestion=item.get('fix_suggestion') or self._suggest_fix(item.get('error_type', ''))
                    )
                    failures.append(failure)
            else:
                # Deterministic fallback: try to guess error types from messages
                for error_msg in test_result.error_messages[:3]:
                    guessed = "Unknown"
                    for et in ["AssertionError", "AttributeError", "TypeError", "ImportError", "ValueError", "ZeroDivisionError", "KeyError", "IndexError"]:
                        if et in error_msg:
                            guessed = et
                            break
                    failures.append(FailureDetail(
                        test_name="Unknown",
                        error_type=guessed,
                        error_message=error_msg,
                        fix_suggestion=self._suggest_fix(guessed)
                    ))
        
        return failures
    
    def _suggest_fix(self, error_type: str) -> str:
        """Generate fix suggestion based on error type"""
        suggestions = {
            "AssertionError": "Review the assertion logic and expected values",
            "TypeError": "Check data types being passed to functions",
            "ValueError": "Validate input values and ranges",
            "ZeroDivisionError": "Add check for zero before division",
            "ImportError": "Verify all required modules are installed",
            "AttributeError": "Check if object has the attribute being accessed",
            "KeyError": "Verify dictionary key exists before accessing",
            "IndexError": "Check list bounds before accessing index"
        }
        return suggestions.get(error_type, "Review the error message and fix accordingly")
    
    def _generate_suggestions(
        self,
        test_result: TestResult,
        failures: list
    ) -> list:
        """Generate actionable suggestions"""
        suggestions = []
        
        if test_result.status == TestStatus.NO_TESTS:
            suggestions.append("Add test files (test_*.py) to the project")
            suggestions.append("Ensure tests are discoverable by pytest")
        
        elif test_result.status == TestStatus.TIMEOUT:
            suggestions.append("Optimize test execution time")
            suggestions.append("Check for infinite loops in code")
        
        elif test_result.status == TestStatus.ERROR:
            suggestions.append("Fix syntax or import errors first")
            suggestions.append("Ensure all dependencies are installed")
        
        elif failures:
            # Add specific suggestions based on error types
            error_types = set(f.error_type for f in failures)
            
            if "ImportError" in error_types:
                suggestions.append("Install missing dependencies")
            if "ZeroDivisionError" in error_types:
                suggestions.append("Add input validation for division operations")
            if "AssertionError" in error_types:
                suggestions.append("Review test expectations and actual outputs")
            
            suggestions.append(f"Focus on fixing {len(failures)} failed test(s)")
        
        return suggestions if suggestions else ["Review error logs and fix issues"]