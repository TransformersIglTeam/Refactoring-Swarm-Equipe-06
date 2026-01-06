from langchain.tools import BaseTool
from typing import Optional
import json
from pathlib import Path

from src.tools.analysis.PylintRunner import PylintRunner

from src.utils import SandboxSetup

class PylintAnalysisTool(BaseTool):
    name: str = "run_pylint_analysis"
    description: str = (
        "Runs pylint static analysis on a Python file or directory. "
        "Input should be a file path or directory path as string. "
        "Returns JSON-formatted pylint results with issues found."
    )
    timeout: int = 30

    def _run(self, target_path: str) -> str:
        """
        Run pylint analysis on the target path.

        Args:
            target_path: File or directory path to analyze (relative to sandbox root)

        Returns:
            JSON string with analysis results
        """
        # Ensure sandbox is configured
        if SandboxSetup.SANDBOX_ROOT is None:
            return "Error: Sandbox not initialized"

        try:
            # Resolve path relative to sandbox root
            resolved_path = Path(SandboxSetup.SANDBOX_ROOT) / target_path
            resolved_path = resolved_path.resolve()
            
            # Validate path is within sandbox
            if not str(resolved_path).startswith(str(Path(SandboxSetup.SANDBOX_ROOT).resolve())):
                return f"Error: Path {target_path} is outside sandbox"
            
            if not resolved_path.exists():
                return f"Error: Path {target_path} does not exist"
            
            runner = PylintRunner(timeout=self.timeout)
            result = runner.run_analysis(str(resolved_path))
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error running pylint analysis: {str(e)}"

class DocstringAnalysisTool(BaseTool):
    name: str = "analyze_docstrings"
    description: str = (
        "Analyzes Python files for missing or incomplete docstrings. "
        "Input should be a file path or directory path as string. "
        "Returns analysis of documentation coverage."
    )

    def _run(self, target_path: str) -> str:
        """
        Analyze docstrings in the target path.

        Args:
            target_path: File or directory path to analyze (relative to sandbox root)

        Returns:
            JSON string with docstring analysis results
        """
        # Ensure sandbox is configured
        if SandboxSetup.SANDBOX_ROOT is None:
            return "Error: Sandbox not initialized"

        try:
            # Use AST to analyze docstrings
            import ast
            import os

            # Resolve path relative to sandbox root
            resolved_path = Path(SandboxSetup.SANDBOX_ROOT) / target_path
            resolved_path = resolved_path.resolve()
            
            # Validate path is within sandbox
            if not str(resolved_path).startswith(str(Path(SandboxSetup.SANDBOX_ROOT).resolve())):
                return f"Error: Path {target_path} is outside sandbox"
            
            if not resolved_path.exists():
                return f"Error: Path {target_path} does not exist"

            results = {
                "files_analyzed": 0,
                "missing_docstrings": [],
                "incomplete_docstrings": [],
                "errors": []
            }

            if resolved_path.is_file() and resolved_path.suffix == '.py':
                files_to_check = [resolved_path]
            elif resolved_path.is_dir():
                files_to_check = []
                # Convert Path to string for os.walk
                for root, dirs, files in os.walk(str(resolved_path)):
                    for file in files:
                        if file.endswith('.py'):
                            files_to_check.append(Path(root) / file)
            else:
                return f"Error: Invalid path {target_path}"

            for file_path in files_to_check:
                try:
                    # Convert Path to string for file operations
                    file_path_str = str(file_path)
                    with open(file_path_str, 'r', encoding='utf-8') as f:
                        content = f.read()

                    tree = ast.parse(content, filename=file_path_str)

                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                            if not ast.get_docstring(node):
                                # Use relative path from sandbox root for display
                                rel_path = os.path.relpath(file_path_str, SandboxSetup.SANDBOX_ROOT)
                                results["missing_docstrings"].append({
                                    "file": rel_path,
                                    "type": type(node).__name__,
                                    "name": getattr(node, 'name', '<module>'),
                                    "line": node.lineno
                                })

                    results["files_analyzed"] += 1

                except Exception as e:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": str(e)
                    })
                    continue

            return json.dumps(results, indent=2)

        except Exception as e:
            return f"Error analyzing docstrings: {str(e)}"