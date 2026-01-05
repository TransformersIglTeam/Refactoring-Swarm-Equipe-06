from pathlib import Path
from typing import Union

def validate_path(file_path: Union[str, Path], root_dir: Union[str, Path]) -> bool:
    """
    Validate that a requested file path is safe inside the sandbox.

    Args:
        file_path (str | Path): user-requested file path
        root_dir (str | Path): sandbox root directory

    Returns:
        bool: True if safe, False if dangerous
    """

    # Resolve both paths to absolute
    root_dir = Path(root_dir).resolve()
    file_path = Path(root_dir / file_path).resolve()

    # 1️⃣ Check if file is inside the sandbox root
    try:
        file_path.relative_to(root_dir)
    except ValueError:
        # File is outside root_dir → dangerous
        return False

    # 2️⃣ Only allow .py files
    if file_path.suffix != ".py":
        return False

    # ✅ Safe path
    return True
