from pathlib import Path
from typing import Union
from utils.logger import log_experiment, ActionType

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
        log_experiment(
            agent_name="SandboxValidator",
            model_used="N/A",
            action=ActionType.FIX,
            details={
                "input_prompt": str(file_path),
                "output_response": "Path traversal attempt detected"
            },
            status="FAILURE"
        )
        return False

    # 2️⃣ Only allow .py files
    if file_path.suffix != ".py":
        log_experiment(
            agent_name="SandboxValidator",
            model_used="N/A",
            action=ActionType.FIX,
            details={
                "input_prompt": str(file_path),
                "output_response": f"Blocked non-Python file ({file_path.suffix})"
            },
            status="FAILURE"
        )
        return False

    # ✅ Safe path
    log_experiment(
        agent_name="SandboxValidator",
        model_used="N/A",
        action=ActionType.FIX,
        details={
            "input_prompt": str(file_path),
            "output_response": "Path validated successfully"
        },
        status="SUCCESS"
    )
    return True
