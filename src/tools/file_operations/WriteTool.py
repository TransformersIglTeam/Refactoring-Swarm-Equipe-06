from langchain.tools import BaseTool
from pathlib import Path
from typing import Optional
import tempfile
import shutil
import ast
import os

from .PathValidator import validate_path
from . import SandboxSetup


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
        # sensible defaults
        self.max_file_size = 5 * 1024 * 1024  # 5 MB
        self.validate_python = True

    def _validate_python_syntax(self, content: str) -> tuple[bool, str]:
        """Validate Python syntax for given content using ast.parse."""
        try:
            ast.parse(content)
            return True, ""
        except SyntaxError as e:
            return False, str(e)

    def _write_atomically(self, path: Path, content: str) -> tuple[bool, str]:
        """Write content to a temp file then atomically replace the destination.

        Returns (success: bool, message: str).
        """
        tmp_file = None
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            # create temp file in same directory for atomic replace
            fd, tmp_name = tempfile.mkstemp(dir=str(path.parent))
            tmp_file = tmp_name
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(content)

            # atomically replace
            os.replace(tmp_name, str(path))
            return True, ""
        except Exception as e:
            # cleanup temp file if present
            try:
                if tmp_file and os.path.exists(tmp_file):
                    os.remove(tmp_file)
            except Exception:
                pass
            return False, str(e)

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
        # Ensure sandbox is configured
        if SandboxSetup.SANDBOX_ROOT is None:
            return "Error: Sandbox not initialized"

        # Validate path (PathValidator enforces .py and containment)
        try:
            ok = validate_path(file_path, SandboxSetup.SANDBOX_ROOT)
        except Exception as e:
            return f"Error validating path: {e}"

        if not ok:
            return f"Error: Unsafe or invalid file path: {file_path}"

        # Convert to Path object under sandbox
        path = Path(SandboxSetup.SANDBOX_ROOT) / file_path
        path = path.resolve()
        
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