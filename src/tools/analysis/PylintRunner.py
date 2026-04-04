import subprocess
import os 


class PylintRunner:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
    def run_analysis(self, target_path: str) -> dict:
        """Run pylint on target path. Path is normalized to absolute for cross-platform consistency."""
        target_path = os.path.abspath(target_path)
        command = [
            "pylint",
            target_path,
            "--output-format=json",
        ]


        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return {"stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode}
        except subprocess.TimeoutExpired:
            return {"error": "Pylint execution timed out."}
        except Exception as e:
            return {"error": str(e)}
