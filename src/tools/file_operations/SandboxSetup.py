from pathlib import Path
from typing import Optional
from utils.logger import log_experiment, ActionType


SANDBOX_ROOT: Optional[Path] = None



def setup_project_sandbox(project_root):
    """
    Initialize the secure sandbox environment.

    Args:
        project_root (str | Path): Path to the Python project.

    Returns:
        Path: validated absolute sandbox path
    """

    global SANDBOX_ROOT

    # 1️⃣ Resolve absolute path
    root = Path(project_root).resolve()

    # 2️⃣ Validate directory
    if not root.exists() or not root.is_dir():
        log_experiment(
            agent_name="SandboxManager",
            model_used="N/A",
            action=ActionType.FIX,
            details={
                "input_prompt": f"setup_project_sandbox({project_root})",
                "output_response": "Project directory not found"
            },
            status="FAILURE"
        )
        raise FileNotFoundError(f"Project root does not exist: {root}")

    # 3️⃣ Store globally
    SANDBOX_ROOT = root

    # 4️⃣ Backup folder
    backup_dir = root / "_sandbox_backup"
    backup_dir.mkdir(exist_ok=True)

    # 5️⃣ Logs folder
    logs_dir = root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # 5️⃣ Log success using your logger
    log_experiment(
        agent_name="SandboxManager",
        model_used="N/A",
        action=ActionType.FIX,
        details={
            "input_prompt": f"setup_project_sandbox({project_root})",
            "output_response": f"Sandbox initialized at {root}"
        },
        status="SUCCESS"
    )

    return SANDBOX_ROOT
