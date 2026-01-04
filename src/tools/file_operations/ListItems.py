from langchain.tools import BaseTool
from pathlib import Path
from typing import List, Optional

from . import SandboxSetup


class ListItems(BaseTool):
    """
    Tool that lists items in a directory.

    Notes:
    - Input: a directory path string.
    - Output: newline-separated names of items, or an error message.
    """

    name = "list items"
    description: str = (
        "Lists items in a directory. Input should be a directory path string. "
        "Returns a newline-separated list of entries or an error message."
    )

    def _run(self, dir_path: str) -> str:
        """
        List items in the given directory path.

        Args:
            dir_path: Path to the directory to list.

        Returns:
            Newline-separated string of entry names, or an error message string.
        """
        # Ensure sandbox is configured
        if SandboxSetup.SANDBOX_ROOT is None:
            return "Error: Sandbox not initialized"

        # Resolve against sandbox root and ensure containment
        try:
            p = (Path(SandboxSetup.SANDBOX_ROOT) / dir_path).resolve()
        except Exception as e:
            return f"Error resolving path: {e}"

        try:
            p.relative_to(Path(SandboxSetup.SANDBOX_ROOT))
        except Exception:
            return f"Error: Path outside sandbox: {dir_path}"

        if not p.exists() or not p.is_dir():
            return f"Error listing directory: not a directory: {dir_path}"

        try:
            entries = [item.name for item in p.iterdir()]
            entries.sort()
            return "\n".join(entries)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    async def _arun(self, dir_path: str) -> str:
        """Async wrapper that delegates to the synchronous implementation."""
        return self._run(dir_path)
