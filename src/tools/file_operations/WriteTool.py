from langchain.tools import BaseTool
from pathlib import Path
from typing import Optional
import tempfile
import shutil
import ast


class WriteTool(BaseTool):
    name = "write file"
    description: str = (
        "Writes content to a file. "
        "Input should be a JSON string with 'file_path' and 'content' keys. "
        "Example: {\"file_path\": \"path/to/file.py\", \"content\": \"print('hello')\"} "
        "Creates parent directories if they don't exist."
    )
    create_backup: bool = True

    def __init__(
        self, 
        create_backup: bool = True
    ):
        """
        Initialize the WriteFileTool.
        
        Args:
            max_file_size: Maximum file size in bytes (default: 5MB)
            validate_python: Validate Python syntax before writing (default: True)
            create_backup: Create backup of existing files (default: True)
        """
        super().__init__()
        self.create_backup = create_backup

    def _create_backup(self, file_path: Path) -> Optional[str]:
        """
        Create a timestamped backup of existing file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file or None if file doesn't exist
        """
        if not file_path.exists():
            return None
        
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.parent / f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
            shutil.copy2(file_path, backup_path)
            return str(backup_path)
        except Exception as e:
            return f"Backup failed: {str(e)}"

    def _run(self, file_path: str, content: str) -> str:
        """
        Write content to file with safety checks.
        
        Args:
            file_path: Path where to write the file
            content: Content to write to the file
            
        Returns:
            Success message or error description
        """
        # Convert to Path object
        path = Path(file_path)
        
        # Check content size
        content_size = len(content.encode('utf-8'))
        if content_size > self.max_file_size:
            size_mb = content_size / 1_048_576
            max_mb = self.max_file_size / 1_048_576
            return f"Error: Content too large ({size_mb:.2f}MB). Maximum: {max_mb:.2f}MB"
        
        # Validate Python syntax if it's a .py file and validation is enabled
        if self.validate_python and path.suffix == '.py':
            is_valid, error_msg = self._validate_python_syntax(content)
            if not is_valid:
                return f"Error: Invalid Python syntax - {error_msg}"
        
        # Create backup if file exists and backup is enabled
        backup_info = ""
        if self.create_backup and path.exists():
            backup_path = self._create_backup(path)
            if backup_path:
                backup_info = f" (Backup created: {backup_path})"
        
        # Write file atomically
        try:
            success, message = self._write_atomically(path, content)
            
            if success:
                file_size = path.stat().st_size
                return f"Success: Wrote {file_size} bytes to {file_path}{backup_info}"
            else:
                return f"Error: {message}"
                
        except PermissionError:
            return f"Error: Permission denied writing to file: {file_path}"
        
        except Exception as e:
            return f"Error writing file: {str(e)}"
    

    def _arun(self, file_path: str, content: str) -> str:
        """
        Async version - not implemented.
        
        Args:
            file_path: Path where to write the file
            content: Content to write to the file
            
        Raises:
            NotImplementedError: Async writing not supported
        """
        raise NotImplementedError("Async writing not implemented")