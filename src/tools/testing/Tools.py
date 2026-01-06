from langchain.tools import BaseTool
from typing import Any
import json

from .PytestRunner import PytestRunner
from .TestParser import TestParser


class PytestTool(BaseTool):
    name = "run pytest"
    description = (
        "Run pytest in a target directory. Input should be a JSON string with 'target_dir' "
        "and optional 'timeout' (seconds). Returns a JSON string with keys: success, stdout, stderr, "
        "execution_time, summary (passed/failed/total), errors (list)."
    )

    def __init__(self, timeout: int = 60):
        super().__init__()
        self.runner = PytestRunner(timeout=timeout)

    def _run(self, input_data: str) -> str:
        try:
            success, stdout, stderr, exec_time = self.runner.run_from_input(input_data)
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

        passed, failed, total = TestParser.parse_summary(stdout + "\n" + stderr)
        errors = TestParser.extract_errors(stdout + "\n" + stderr)

        result = {
            "success": success,
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": exec_time,
            "summary": {"passed": passed, "failed": failed, "total": total},
            "errors": errors,
        }
        return json.dumps(result)

    async def _arun(self, input_data: str) -> str:
        return self._run(input_data)
