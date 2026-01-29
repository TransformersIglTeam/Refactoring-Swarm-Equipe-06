import json
import os
import uuid
from datetime import datetime
from enum import Enum

# Path to the log file
LOG_FILE = os.path.join("logs", "experiment_data.json")


class ActionType(str, Enum):
    """
    Enumeration of possible action types for standardizing analysis.
    """
    ANALYSIS = "CODE_ANALYSIS"   # Audit, read, bug search
    GENERATION = "CODE_GEN"     # Create new code/tests/docs
    DEBUG = "DEBUG"             # Runtime error analysis
    FIX = "FIX"                 # Apply fixes


def log_experiment(agent_name: str, model_used: str, action: ActionType, details: dict, status: str) -> None:
    """
    Log an agent interaction for analysis.

    Args:
        agent_name: Name of the agent (e.g. "Auditor", "Fixer").
        model_used: LLM model used (e.g. "gemini-1.5-flash").
        action: Type of action performed (use ActionType enum).
        details: Dict with details. MUST contain 'input_prompt' and 'output_response'.
        status: "SUCCESS" or "FAILURE".

    Raises:
        ValueError: If required keys are missing in 'details' or action is invalid.
    """
    # --- 1. ACTION TYPE VALIDATION ---
    valid_actions = [a.value for a in ActionType]
    if isinstance(action, ActionType):
        action_str = action.value
    elif action in valid_actions:
        action_str = action
    else:
        raise ValueError(
            f"Invalid action: '{action}'. Use ActionType (e.g. ActionType.FIX)."
        )

    # --- 2. STRICT DATA VALIDATION (Prompts) ---
    if action_str in [ActionType.ANALYSIS, ActionType.GENERATION, ActionType.DEBUG, ActionType.FIX]:
        required_keys = ["input_prompt", "output_response"]
        missing_keys = [key for key in required_keys if key not in details]
        if missing_keys:
            raise ValueError(
                f"Logging error (Agent: {agent_name}): "
                f"Missing required keys in 'details': {missing_keys}."
            )

    # --- 3. PREPARE ENTRY ---
    os.makedirs("logs", exist_ok=True)
    entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "model": model_used,
        "action": action_str,
        "details": details,
        "status": status
    }

    # --- 4. ROBUST READ & WRITE ---
    data = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: Log file {LOG_FILE} was corrupted. Starting with empty list.")
            data = []

    data.append(entry)
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)