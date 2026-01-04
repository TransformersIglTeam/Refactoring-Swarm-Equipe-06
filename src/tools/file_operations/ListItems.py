from langchain.tools import BaseTool
from pathlib import Path
from typing import List, Optional


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
        p = Path(dir_path)
        try:
            # Intentionally do not pre-validate path (no .exists() / .is_dir()).
            entries = [item.name for item in p.iterdir()]
            entries.sort()
            return "\n".join(entries)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

    async def _arun(self, dir_path: str) -> str:
        """Async wrapper that delegates to the synchronous implementation."""
        return self._run(dir_path)
