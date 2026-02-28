import os
from typing import List
from src.tools.testing.PytestRunner import PytestRunner
from src.tools.testing.TestParser import TestParser
from src.agents.judge.Models import TestResult, TestStatus
from src.utils.logger import log_experiment, ActionType


class TestExecutor:
    """Executes tests and builds TestResult objects"""
    
    def __init__(self, agent_name: str = "Judge_Agent", model_name: str = "gemini-2.5-flash"):
        self.agent_name = agent_name
        self.model_name = model_name
        self.runner = PytestRunner()
        self.parser = TestParser()
    
    def execute(self, target_dir: str) -> TestResult:
        """
        Execute tests on target directory
        
        Args:
            target_dir: Directory containing code to test
            
        Returns:
            TestResult object with all execution details
        """
        # Check if directory exists
        if not os.path.exists(target_dir):
            return self._create_error_result(
                f"Directory not found: {target_dir}",
                TestStatus.ERROR
            )
        
        # Find test files
        test_files = self._find_test_files(target_dir)
        
        if not test_files:
            log_experiment(
                agent_name=self.agent_name,
                model_used=self.model_name,
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": f"Looking for test files in {target_dir}",
                    "output_response": "No test files found",
                    "target_dir": target_dir
                },
                status="NO_TESTS"
            )
            
            return TestResult(
                status=TestStatus.NO_TESTS,
                error_messages=["No test files found in directory"]
            )
        
        # Log test execution start
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Execute pytest on {len(test_files)} test file(s)",
                "output_response": f"Found tests: {[os.path.basename(f) for f in test_files]}",
                "target_dir": target_dir,
                "test_files_count": len(test_files)
            },
            status="RUNNING"
        )
        
        # Run tests
        success, stdout, stderr, exec_time = self.runner.run(target_dir)
        
        # Handle errors
        if stderr and not stdout:
            return self._handle_execution_error(stderr, exec_time)
        
        # Parse results
        passed, failed, total = self.parser.parse_summary(stdout)
        errors = self.parser.extract_errors(stdout)
        
        # Determine status
        if success and passed > 0:
            status = TestStatus.SUCCESS
        elif failed > 0:
            status = TestStatus.FAILED
        else:
            status = TestStatus.ERROR
        
        # Create result object
        result = TestResult(
            status=status,
            tests_passed=passed,
            tests_failed=failed,
            tests_total=total,
            success=success,
            error_messages=errors,
            test_output=stdout,
            execution_time=exec_time
        )
        
        # Log completion
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": f"Validate test results for {target_dir}",
                "output_response": f"Tests completed: {passed} passed, {failed} failed",
                "tests_passed": passed,
                "tests_failed": failed,
                "execution_time": exec_time
            },
            status="SUCCESS" if success else "FAILED"
        )
        
        return result
    
    def _find_test_files(self, directory: str) -> List[str]:
        """Find all test files in directory"""
        test_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if (file.startswith("test_") or file.endswith("_test.py")) and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        return test_files
    
    def _create_error_result(self, error_message: str, status: TestStatus) -> TestResult:
        """Create a TestResult for error cases"""
        return TestResult(
            status=status,
            error_messages=[error_message]
        )
    
    def _handle_execution_error(self, stderr: str, exec_time: float) -> TestResult:
        """Handle execution errors"""
        if "Timeout" in stderr:
            status = TestStatus.TIMEOUT
        elif "not installed" in stderr:
            status = TestStatus.ERROR
            stderr = "pytest is not installed. Run: pip install pytest"
        else:
            status = TestStatus.ERROR
        
        log_experiment(
            agent_name=self.agent_name,
            model_used=self.model_name,
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Execute tests",
                "output_response": f"Execution error: {stderr}",
                "error": stderr
            },
            status="ERROR"
        )
        
        return TestResult(
            status=status,
            error_messages=[stderr],
            execution_time=exec_time
        )