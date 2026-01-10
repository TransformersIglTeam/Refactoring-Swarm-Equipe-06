"""
Test runner utilities for executing unit tests.
"""

import os
import subprocess
import logging
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TestFramework(Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"


@dataclass
class TestRunResult:
    """Result of a test run."""
    success: bool
    output: str
    framework_used: TestFramework
    error: Optional[str] = None


class TestRunner:
    """Runs unit tests for a project."""
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    
    def __init__(self, project_path: str, timeout: int = DEFAULT_TIMEOUT):
        self.project_path = os.path.abspath(project_path)
        self.timeout = timeout
        self._env = self._build_environment()
    
    def run(self, test_directory: str) -> TestRunResult:
        """
        Run tests in the specified directory.
        
        Args:
            test_directory: Path to the directory containing tests.
            
        Returns:
            TestRunResult with the test execution results.
        """
        # Try pytest first, fall back to unittest
        result = self._run_pytest(test_directory)
        
        if result.error and "No module named pytest" in result.error:
            logger.info("pytest not available, falling back to unittest")
            result = self._run_unittest(test_directory)
        
        return result
    
    def _run_pytest(self, test_directory: str) -> TestRunResult:
        """Run tests using pytest."""
        cmd = [
            "python", "-m", "pytest",
            test_directory,
            "-v",
            "--tb=short"
        ]
        return self._execute_test_command(cmd, TestFramework.PYTEST)
    
    def _run_unittest(self, test_directory: str) -> TestRunResult:
        """Run tests using unittest."""
        cmd = [
            "python", "-m", "unittest",
            "discover",
            "-s", test_directory,
            "-v"
        ]
        return self._execute_test_command(cmd, TestFramework.UNITTEST)
    
    def _execute_test_command(
        self, 
        cmd: list, 
        framework: TestFramework
    ) -> TestRunResult:
        """Execute a test command and return the result."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.project_path,
                env=self._env
            )
            
            output = result.stdout + result.stderr
            success = result.returncode == 0
            
            return TestRunResult(
                success=success,
                output=output,
                framework_used=framework
            )
            
        except subprocess.TimeoutExpired:
            return TestRunResult(
                success=False,
                output="",
                framework_used=framework,
                error=f"Test execution timed out after {self.timeout}s"
            )
        except FileNotFoundError as e:
            return TestRunResult(
                success=False,
                output="",
                framework_used=framework,
                error=str(e)
            )
        except Exception as e:
            return TestRunResult(
                success=False,
                output="",
                framework_used=framework,
                error=f"Unexpected error: {str(e)}"
            )
    
    def _build_environment(self) -> dict:
        """Build the environment variables for test execution."""
        env = os.environ.copy()
        
        # Add project paths to PYTHONPATH
        python_paths = [
            self.project_path,
            os.path.join(self.project_path, "src")
        ]
        
        existing_pythonpath = env.get("PYTHONPATH", "")
        if existing_pythonpath:
            python_paths.append(existing_pythonpath)
        
        env["PYTHONPATH"] = os.pathsep.join(python_paths)
        
        return env
