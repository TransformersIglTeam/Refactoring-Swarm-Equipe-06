import json
from typing import Optional

from src.agents.judge.TestExecutor import TestExecutor
from src.agents.judge.ResultAnalyzer import ResultAnalyzer
from src.agents.judge.Models import JudgeResult, JudgeDecision, FailureDetail, TestResult
from src.agents.judge.BaseAgent import BaseAgent


class JudgeAgent:
    """
    Main Judge Agent - Orchestrates test execution and analysis
    
    Responsibilities:
    - Execute tests on target directory
    - Analyze results and make decisions
    - Return clean, structured output objects
    
    Usage:
        judge = JudgeAgent()
        result = judge.judge(target_dir="./sandbox/project", iteration=1)
        result.print_summary()  # Console output
        result_dict = result.to_dict()  # For JSON/API
    """
    
    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        max_iterations: int = 3,
    ):
        """
        Initialize Judge Agent
        
        Args:
            model_name: Name of the model for logging
            max_iterations: Maximum retry iterations allowed
        """
        self.agent_name = "Judge_Agent"
        self.model_name = model_name
        self.max_iterations = max_iterations
        
        self.executor = TestExecutor(
            agent_name=self.agent_name,
            model_name=self.model_name
        )
        
        self.analyzer = ResultAnalyzer(
            agent_name=self.agent_name,
            model_name=self.model_name,
            max_iterations=self.max_iterations
        )

        self.base_agent = BaseAgent(model_name=self.model_name)
    
    def judge(self, target_dir: str, iteration: int = 1) -> JudgeResult:
        """
        Main method - Execute tests and make judgment
        
        Args:
            target_dir: Directory containing code to test
            iteration: Current iteration number (for loop tracking)
            
        Returns:
            JudgeResult object with decision and details
            
        Example:
            >>> judge = JudgeAgent()
            >>> result = judge.judge("./sandbox/my_project", iteration=1)
            >>> print(result.decision)  # PASS, RETRY, or MAX_ITERATIONS
            >>> result.print_summary()  # Pretty console output
        """
        # Step 1: Execute tests (the 'tool')
        test_result = self.executor.execute(target_dir)

        # If LLM (Gemini) is available, ask it to analyze the test output and
        # produce structured JSON with decision, failures and suggestions.
        prompt = (
            "You are an automated judge (Gemini). Analyze the pytest output and "
            "return a JSON object with keys: decision, reason, failures, suggestions. "
            "- decision: one of PASS, RETRY, MAX_ITERATIONS.\n"
            "- reason: short human-readable reason.\n"
            "- failures: array of objects with test_name, error_type, error_message, fix_suggestion.\n"
            "- suggestions: array of short suggestion strings.\n"
            "Respond with pure JSON only.\n\n"
            f"TEST_SUMMARY:\nStatus: {test_result.status.value}\nPassed: {test_result.tests_passed}\nFailed: {test_result.tests_failed}\n"
            f"ERROR_MESSAGES:\n{json.dumps(test_result.error_messages)}\n\n"
            f"OUTPUT_EXCERPT:\n{test_result.test_output[:2000]}\n\n"
        )

        llm_response = None
        structured = None
        if self.base_agent and self.base_agent.llm:
            try:
                llm_response = self.base_agent.llm_call(prompt)
                # Log the LLM interaction (non-fatal if logging fails)
                try:
                    from src.utils.logger import log_experiment, ActionType
                    log_experiment(
                        agent_name=self.agent_name,
                        model_used=self.model_name,
                        action=ActionType.ANALYSIS,
                        details={
                            "input_prompt": prompt,
                            "output_response": llm_response or "",
                        },
                        status="SUCCESS" if llm_response else "NO_RESPONSE"
                    )
                except Exception:
                    pass


                if llm_response:
                    try:
                        structured = json.loads(llm_response)
                    except Exception:
                        # try to extract JSON substring
                        try:
                            start = llm_response.index('{')
                            end = llm_response.rindex('}') + 1
                            structured = json.loads(llm_response[start:end])
                        except Exception:
                            structured = None
            except Exception:
                llm_response = None

        if structured and isinstance(structured, dict):
            decision_str = structured.get('decision', 'RETRY')
            try:
                decision = JudgeDecision[decision_str]
            except Exception:
                decision = JudgeDecision.RETRY

            reason = structured.get('reason', f"{test_result.tests_failed} test(s) failed")

            failures_list = []
            for item in structured.get('failures', [])[:10]:
                failures_list.append(FailureDetail(
                    test_name=item.get('test_name', 'Unknown'),
                    error_type=item.get('error_type', 'Unknown'),
                    error_message=item.get('error_message', 'No details available'),
                    fix_suggestion=item.get('fix_suggestion')
                ))

            suggestions = structured.get('suggestions', [])

            return JudgeResult(
                decision=decision,
                test_result=test_result,
                iteration=iteration,
                reason=reason,
                failures=failures_list,
                suggestions=suggestions
            )

        # Fallback: use existing analyzer to create a decision
        return self.analyzer.analyze(test_result, iteration=iteration)
    
    def judge_and_print(self, target_dir: str, iteration: int = 1) -> JudgeResult:
        """
        Convenience method - Judge and print results to console
        
        Args:
            target_dir: Directory to test
            iteration: Current iteration
            
        Returns:
            JudgeResult object
        """
        result = self.judge(target_dir)
        result.print_summary()
        return result