from langchain.tools import BaseTool
from pathlib import Path
from typing import Optional

class WriteTool(BaseTool):
    name = "write file"
    description: str = (
        "Writes content to a file. "
        "Input should be a file path and content as strings. "
        "Creates the file if it doesn't exist, overwrites if it does."
    )

    def _run(self, file_path: str, content: str) -> str:
        """
        Write content to the given file path.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            
        Returns:
            Success message or error message
        """

        path = Path(file_path)
        
        # Ensure parent directories exist
        if not path.parent.exists():
            return f"Error: The parent directory {path.parent} does not exist."
        
        if path.is_dir():
            return f"Error: Path is a directory, not a file: {file_path}"
        
        try:
            with path.open("w", encoding="utf-8") as file:
                file.write(content)
            return f"Successfully wrote to file: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def _arun(self, file_path: str, content: str) -> str:
        """Asynchronous write of content to a file."""
        return self._run(file_path, content)
