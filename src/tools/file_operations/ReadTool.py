from langchain.tools import BaseTool
from pathlib import Path
from typing import Optional

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

        path = Path(file_path)
        if not path.is_file():
            return f"Error: The file at {file_path} does not exist."
        
        if not path.is_file():
            return f"Error: Path is not a file: {file_path}"
        try:
            with path.open("r", encoding="utf-8") as file:
                content = file.read()
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def _arun(self, file_path: str) -> str:
        """Asynchronous read of the contents of a file."""
        return self._run(file_path)