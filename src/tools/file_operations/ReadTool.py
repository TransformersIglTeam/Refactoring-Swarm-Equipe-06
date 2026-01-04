from langchain.tools import BaseTool
from pathlib import Path
from typing import Optional

from .PathValidator import validate_path
from . import SandboxSetup

class ReadTool(BaseTool):
    name = "read file"
    description: str = (
        "Reads and returns the content of a file. "
        "Input should be a file path as string. "
        "Returns the file content as text."
    )

    def _run(self, file_path: str) -> str:
        """
        Read file content from the given path.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string or error message
        """

        # Ensure sandbox is configured
        if SandboxSetup.SANDBOX_ROOT is None:
            return "Error: Sandbox not initialized"

        # Validate path against sandbox rules
        try:
            ok = validate_path(file_path, SandboxSetup.SANDBOX_ROOT)
        except Exception as e:
            return f"Error validating path: {e}"

        if not ok:
            return f"Error: Unsafe or invalid file path: {file_path}"

        path = Path(SandboxSetup.SANDBOX_ROOT) / file_path
        path = path.resolve()

        if not path.is_file():
            return f"Error: The file at {file_path} does not exist."

        try:
            with path.open("r", encoding="utf-8") as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def _arun(self, file_path: str) -> str:
        """Asynchronous read of the contents of a file."""
        return self._run(file_path)