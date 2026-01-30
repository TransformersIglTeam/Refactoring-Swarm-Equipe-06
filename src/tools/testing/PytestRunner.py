import subprocess
import time
import sys
import json
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


class PytestRunner:
    """Handles low-level pytest execution"""
    
    def __init__(self, timeout: int = 60):
        self.timeout = timeout
    
    def run(self, target_dir: str) -> Tuple[bool, str, str, float]:
        """
        Execute pytest on target directory
        
        Args:
            target_dir: Project Directory to test
            
        Returns:
            Tuple of (success, stdout, stderr, execution_time)
        """
        start_time = time.time()
        logger.info(f"Starting pytest run in: {target_dir} with timeout: {self.timeout}s")

        # Use the current Python executable to ensure the venv's pytest is used
        cmd = [sys.executable, "-m", "pytest", target_dir, "-v", "--tb=short", "--color=no"]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            execution_time = time.time() - start_time
            success = result.returncode == 0

            # If pytest module isn't installed, stderr typically contains "No module named pytest"
            if not success and ("No module named pytest" in (result.stderr or "") or "ModuleNotFoundError: No module named 'pytest'" in (result.stderr or "")):
                return False, result.stdout, "pytest not installed in this Python environment", execution_time

            return success, result.stdout, result.stderr, execution_time

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return False, "", f"Timeout after {self.timeout}s", execution_time

        except Exception as e:
            execution_time = time.time() - start_time
            return False, "", str(e), execution_time

    def run_from_input(self, input_data: Union[str, dict]) -> Tuple[bool, str, str, float]:
        """
        Convenience wrapper that accepts either a dict or a JSON string with keys:
        - target_dir: path to run pytest in
        - timeout: optional seconds override

        Returns same tuple as `run`.
        """
        if isinstance(input_data, dict):
            target_dir = input_data.get("target_dir")
            timeout = input_data.get("timeout")
        else:
            try:
                payload = json.loads(input_data)
                target_dir = payload.get("target_dir")
                timeout = payload.get("timeout")
            except Exception:
                # fallback parsing: allow 'dir::timeout'
                if isinstance(input_data, str) and "::" in input_data:
                    target_dir, timeout_s = input_data.split("::", 1)
                    try:
                        timeout = int(timeout_s)
                    except Exception:
                        timeout = None
                else:
                    return False, "", "Invalid input to run_from_input", 0.0

        if not target_dir:
            return False, "", "Missing target_dir", 0.0

        # temporarily override timeout if provided
        if timeout:
            old = self.timeout
            self.timeout = int(timeout)
            try:
                return self.run(target_dir)
            finally:
                self.timeout = old
        else:
            return self.run(target_dir)