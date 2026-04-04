# Micro-Refactoring Checklist for Refactoring Swarm

This document contains isolated, non-logic-changing refactoring opportunities found across the codebase.

---

## ✅ Checklist

### 1. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/analysis/PylintRunner.py`
   - **Line**: 6
   - **Issue**: `__init__` method missing return type annotation (`-> None`)
   - **Current**: `def __init__(self,timeout = 30):`
   - **Suggested**: `def __init__(self, timeout: int = 30) -> None:`

### 2. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/analysis/PylintRunner.py`
   - **Line**: 8
   - **Issue**: `run_analysis` method missing return type annotation
   - **Current**: `def run_analysis(self,target_path):`
   - **Suggested**: `def run_analysis(self, target_path: str) -> dict:`

### 3. **Code Style: Remove inline comment in code**
   - **File**: `src/tools/analysis/PylintRunner.py`
   - **Line**: 8
   - **Issue**: Inline comment in Arabic/French should be moved to docstring
   - **Current**: `def run_analysis(self,target_path): # hada ydir path -> abs path bach nevitiw les problem t3 windows`
   - **Suggested**: Move explanation to method docstring

### 4. **Code Style: Remove commented-out code**
   - **File**: `src/tools/analysis/PylintRunner.py`
   - **Line**: 13
   - **Issue**: Commented-out code should be removed
   - **Current**: `#"--rcfile=.pylintrc" m7bsh ymchi hada (lazmlou logic of either creating a file or already in repo)`
   - **Suggested**: Remove or convert to TODO comment

### 5. **Type Hint: Missing type annotations**
   - **File**: `src/tools/analysis/PylintParser.py`
   - **Line**: 5
   - **Issue**: `__init__` method missing type hints for parameters
   - **Current**: `def __init__(self, issues, score=0.0):`
   - **Suggested**: `def __init__(self, issues: list, score: float = 0.0) -> None:`

### 6. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/analysis/PylintParser.py`
   - **Line**: 11
   - **Issue**: `get_critical_issues` missing return type
   - **Current**: `def get_critical_issues(self):`
   - **Suggested**: `def get_critical_issues(self) -> list:`

### 7. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/analysis/PylintParser.py`
   - **Line**: 16
   - **Issue**: `parse` method missing return type annotation
   - **Current**: `def parse(self, raw_json):`
   - **Suggested**: `def parse(self, raw_json: str) -> PylintResult:`

### 8. **Code Style: Remove unused variable**
   - **File**: `src/tools/analysis/PylintParser.py`
   - **Line**: 25-28
   - **Issue**: Empty lines and unnecessary whitespace in loop
   - **Current**: Multiple blank lines before `parsed_issues.append`
   - **Suggested**: Clean up formatting

### 9. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/file_operations/ReadTool.py`
   - **Line**: 9
   - **Issue**: Class attribute `name` should have type annotation
   - **Current**: `name = "read file"`
   - **Suggested**: `name: str = "read file"`

### 10. **Type Hint: Unused import**
   - **File**: `src/tools/file_operations/ReadTool.py`
   - **Line**: 3
   - **Issue**: `Optional` imported but not used
   - **Current**: `from typing import Optional`
   - **Suggested**: Remove unused import

### 11. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/file_operations/WriteTool.py`
   - **Line**: 34
   - **Issue**: `_validate_python_syntax` return type uses `tuple[bool, str]` (Python 3.9+ syntax) but should use `Tuple` from typing for compatibility
   - **Current**: `def _validate_python_syntax(self, content: str) -> tuple[bool, str]:`
   - **Suggested**: Import `Tuple` and use `Tuple[bool, str]` or verify Python version requirement

### 12. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/file_operations/WriteTool.py`
   - **Line**: 42
   - **Issue**: `_write_atomically` return type uses `tuple[bool, str]` - same as above
   - **Current**: `def _write_atomically(self, path: Path, content: str) -> tuple[bool, str]:`
   - **Suggested**: Use `Tuple[bool, str]` from typing

### 13. **Type Hint: Unused import**
   - **File**: `src/tools/file_operations/WriteTool.py`
   - **Line**: 3
   - **Issue**: `Type` imported but not used in the file
   - **Current**: `from typing import Optional, Type`
   - **Suggested**: Remove `Type` if not used (verify `args_schema` usage)

### 14. **Code Style: Inconsistent variable naming**
   - **File**: `src/tools/file_operations/WriteTool.py`
   - **Line**: 33
   - **Issue**: Variable `ok` is not descriptive
   - **Current**: `ok = validate_path(file_path, SandboxSetup.SANDBOX_ROOT)`
   - **Suggested**: `is_valid_path = validate_path(...)`

### 15. **Docstring: Enhance docstring**
   - **File**: `src/tools/file_operations/ListItems.py`
   - **Line**: 7-14
   - **Issue**: Docstring uses "Notes:" format instead of standard docstring format
   - **Current**: Uses `Notes:` section
   - **Suggested**: Convert to standard Args/Returns format or enhance with Args/Returns sections

### 16. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/testing/PytestRunner.py`
   - **Line**: 11
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, timeout: int = 60):`
   - **Suggested**: `def __init__(self, timeout: int = 60) -> None:`

### 17. **Code Style: Modernize tuple return type**
   - **File**: `src/tools/testing/PytestRunner.py`
   - **Line**: 14
   - **Issue**: Uses `Tuple` from typing, could use `tuple` (Python 3.9+)
   - **Current**: `def run(self, target_dir: str) -> Tuple[bool, str, str, float]:`
   - **Suggested**: `def run(self, target_dir: str) -> tuple[bool, str, str, float]:` (if Python 3.9+)

### 18. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/testing/PytestRunner.py`
   - **Line**: 54
   - **Issue**: `run_from_input` missing return type annotation (has it but uses Union)
   - **Current**: `def run_from_input(self, input_data: Union[str, dict]) -> Tuple[bool, str, str, float]:`
   - **Note**: Already has type hints, but could modernize `Union` to `|` (Python 3.10+)

### 19. **Code Style: Modernize Union syntax**
   - **File**: `src/tools/testing/PytestRunner.py`
   - **Line**: 5
   - **Issue**: Uses `Union` from typing, could use `|` operator (Python 3.10+)
   - **Current**: `from typing import Tuple, Optional, Union`
   - **Suggested**: Use `str | dict` instead of `Union[str, dict]` if Python 3.10+

### 20. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/testing/TestParser.py`
   - **Line**: 95
   - **Issue**: `_parse_failure_section` missing return type annotation
   - **Current**: `def _parse_failure_section(section: str) -> Dict[str, str]:`
   - **Note**: Already has return type, but could modernize `Dict` to `dict` (Python 3.9+)

### 21. **Code Style: Modernize Dict/List/Tuple imports**
   - **File**: `src/tools/testing/TestParser.py`
   - **Line**: 2
   - **Issue**: Uses `List, Dict, Tuple` from typing, could use lowercase (Python 3.9+)
   - **Current**: `from typing import List, Dict, Tuple`
   - **Suggested**: Use `list`, `dict`, `tuple` directly if Python 3.9+

### 22. **Type Hint: Missing return type annotation**
   - **File**: `src/tools/testing/Tools.py`
   - **Line**: 17
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, timeout: int = 60):`
   - **Suggested**: `def __init__(self, timeout: int = 60) -> None:`

### 23. **Type Hint: Unused import**
   - **File**: `src/tools/testing/Tools.py`
   - **Line**: 2
   - **Issue**: `Any` imported but not used
   - **Current**: `from typing import Any`
   - **Suggested**: Remove unused import

### 24. **Code Style: Inconsistent spacing**
   - **File**: `src/utils/SandboxSetup.py`
   - **Line**: 4-6
   - **Issue**: Multiple blank lines between imports and code
   - **Current**: Three blank lines
   - **Suggested**: Standardize to one blank line

### 25. **Type Hint: Missing return type annotation**
   - **File**: `src/utils/SandboxSetup.py`
   - **Line**: 10
   - **Issue**: `setup_project_sandbox` missing return type annotation
   - **Current**: `def setup_project_sandbox(project_root):`
   - **Suggested**: `def setup_project_sandbox(project_root: str | Path) -> Path:`

### 26. **Docstring: Enhance docstring**
   - **File**: `src/utils/SandboxSetup.py`
   - **Line**: 10-18
   - **Issue**: Docstring uses old-style type hints in parentheses
   - **Current**: `project_root (str | Path):`
   - **Suggested**: Update to modern docstring format with proper Args section

### 27. **Code Style: Remove trailing whitespace**
   - **File**: `src/utils/SandboxSetup.py`
   - **Line**: 28
   - **Issue**: Trailing whitespace after `if not root.exists()`
   - **Current**: Line ends with spaces
   - **Suggested**: Remove trailing whitespace

### 28. **Code Style: Remove unnecessary blank lines**
   - **File**: `src/utils/SandboxSetup.py`
   - **Line**: 42-44
   - **Issue**: Unnecessary blank lines before return
   - **Current**: Multiple blank lines
   - **Suggested**: Remove extra blank lines

### 29. **Type Hint: Missing return type annotation**
   - **File**: `src/utils/PathValidator.py`
   - **Line**: 4
   - **Issue**: Function missing return type annotation (has it)
   - **Current**: `def validate_path(file_path: Union[str, Path], root_dir: Union[str, Path]) -> bool:`
   - **Note**: Already has type hints, but could modernize `Union` to `|` (Python 3.10+)

### 30. **Code Style: Modernize Union syntax**
   - **File**: `src/utils/PathValidator.py`
   - **Line**: 2
   - **Issue**: Uses `Union` from typing, could use `|` operator (Python 3.10+)
   - **Current**: `from typing import Union`
   - **Suggested**: Use `str | Path` instead of `Union[str, Path]` if Python 3.10+

### 31. **Docstring: Enhance docstring**
   - **File**: `src/utils/PathValidator.py`
   - **Line**: 4-13
   - **Issue**: Docstring uses old-style type hints in parentheses
   - **Current**: `file_path (str | Path):`
   - **Suggested**: Update to modern docstring format

### 32. **Code Style: Remove French comments**
   - **File**: `src/utils/logger.py`
   - **Line**: 7
   - **Issue**: Comment in French should be in English
   - **Current**: `# Chemin du fichier de logs`
   - **Suggested**: `# Path to the log file`

### 33. **Docstring: Enhance docstring**
   - **File**: `src/utils/logger.py`
   - **Line**: 12-13
   - **Issue**: Docstring in French should be in English
   - **Current**: `Énumération des types d'actions possibles pour standardiser l'analyse.`
   - **Suggested**: `Enumeration of possible action types for standardizing analysis.`

### 34. **Docstring: Enhance docstring**
   - **File**: `src/utils/logger.py`
   - **Line**: 19-31
   - **Issue**: Docstring partially in French, should be fully in English
   - **Current**: Mix of French and English
   - **Suggested**: Translate all French text to English

### 35. **Code Style: Remove French error messages**
   - **File**: `src/utils/logger.py`
   - **Line**: 42, 53-56
   - **Issue**: Error messages contain French text
   - **Current**: `"❌ Action invalide : '{action}'..."`
   - **Suggested**: Translate to English

### 36. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/auditor/AuditorAgent.py`
   - **Line**: 40
   - **Issue**: `_init_agent` missing return type annotation (has it)
   - **Current**: `def _init_agent(self) -> Optional[AgentExecutor]:`
   - **Note**: Already has return type, but could modernize `Optional` to `| None` (Python 3.10+)

### 37. **Code Style: Modernize Optional syntax**
   - **File**: `src/agents/auditor/AuditorAgent.py`
   - **Line**: 2
   - **Issue**: Uses `Optional` from typing, could use `| None` (Python 3.10+)
   - **Current**: `from typing import List, Optional`
   - **Suggested**: Use `AgentExecutor | None` instead of `Optional[AgentExecutor]` if Python 3.10+

### 38. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/auditor/AuditorAgent.py`
   - **Line**: 86
   - **Issue**: `audit` method missing return type annotation
   - **Current**: `def audit(self, project_path: str) -> str:`
   - **Note**: Already has return type annotation

### 39. **Code Style: Inconsistent variable naming**
   - **File**: `src/agents/fixer/FixerAgent.py`
   - **Line**: 63
   - **Issue**: Inconsistent `agent_kwargs` usage - duplicate key
   - **Current**: `agent_kwargs={"system_message": FIXER_SYSTEM_PROMPT, "prefix_messages": "you are a python engineer..."}`
   - **Issue**: `agent_kwargs` defined twice with different keys
   - **Suggested**: Consolidate into single `agent_kwargs` dict

### 40. **Type Hint: Unused import**
   - **File**: `src/agents/fixer/FixerAgent.py`
   - **Line**: 6
   - **Issue**: `GoogleGenerativeAI` imported but not used
   - **Current**: `from langchain_google_genai import GoogleGenerativeAI`
   - **Suggested**: Remove unused import

### 41. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/JudgeAgent.py`
   - **Line**: 55
   - **Issue**: `judge` method missing return type annotation (has it)
   - **Current**: `def judge(self, target_dir: str, iteration: int = 1) -> JudgeResult:`
   - **Note**: Already has return type

### 42. **Code Style: String formatting**
   - **File**: `src/agents/judge/JudgeAgent.py`
   - **Line**: 78
   - **Issue**: String concatenation could use f-string
   - **Current**: `"You are an automated judge . Analyze..."`
   - **Note**: Minor typo: extra space after "judge"

### 43. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/JudgeAgent.py`
   - **Line**: 157
   - **Issue**: `judge_and_print` missing return type annotation (has it)
   - **Current**: `def judge_and_print(self, target_dir: str, iteration: int = 1) -> JudgeResult:`
   - **Note**: Already has return type

### 44. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/BaseAgent.py`
   - **Line**: 21
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key_env: str = "GOOGLE_API_KEY"):`
   - **Suggested**: `def __init__(self, model_name: str = "gemini-2.5-flash-lite", api_key_env: str = "GOOGLE_API_KEY") -> None:`

### 45. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/BaseAgent.py`
   - **Line**: 26
   - **Issue**: `_init_llm` missing return type annotation (has it)
   - **Current**: `def _init_llm(self) -> Optional[Any]:`
   - **Note**: Already has return type, but could modernize `Optional[Any]` to `Any | None` (Python 3.10+)

### 46. **Code Style: Remove dead code**
   - **File**: `src/agents/judge/BaseAgent.py`
   - **Line**: 3
   - **Issue**: `importlib` imported but not used
   - **Current**: `import importlib`
   - **Suggested**: Remove unused import

### 47. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/BaseAgent.py`
   - **Line**: 93
   - **Issue**: `llm_call` missing return type annotation (has it)
   - **Current**: `def llm_call(self, prompt: str) -> Optional[str]:`
   - **Note**: Already has return type, could modernize `Optional[str]` to `str | None`

### 48. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/BaseAgent.py`
   - **Line**: 136
   - **Issue**: `decide` method missing return type annotation (has it)
   - **Current**: `def decide(self, test_summary: str, tests_failed: int, tests_passed: int) -> str:`
   - **Note**: Already has return type

### 49. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/TestExecutor.py`
   - **Line**: 12
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, agent_name: str = "Judge_Agent", model_name: str = "gemini-2.5-flash"):`
   - **Suggested**: `def __init__(self, agent_name: str = "Judge_Agent", model_name: str = "gemini-2.5-flash") -> None:`

### 50. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/TestExecutor.py`
   - **Line**: 18
   - **Issue**: `execute` method missing return type annotation (has it)
   - **Current**: `def execute(self, target_dir: str) -> TestResult:`
   - **Note**: Already has return type

### 51. **Type Hint: Missing return type annotation**
   - **File**: `src/agents/judge/ResultAnalyzer.py`
   - **Line**: 17
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, agent_name: str = "Judge_Agent", model_name: str = "gemini-2.5-flash", max_iterations: int = 10):`
   - **Suggested**: `def __init__(self, agent_name: str = "Judge_Agent", model_name: str = "gemini-2.5-flash", max_iterations: int = 10) -> None:`

### 52. **Code Style: String literal bug**
   - **File**: `src/agents/judge/ResultAnalyzer.py`
   - **Line**: 184
   - **Issue**: String literal `"self.agent_name"` instead of variable `self.agent_name`
   - **Current**: `agent_name="self.agent_name",`
   - **Suggested**: `agent_name=self.agent_name,`

### 53. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/orchestrator.py`
   - **Line**: 28
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, max_iterations: int = DEFAULT_MAX_ITERATIONS,):`
   - **Suggested**: `def __init__(self, max_iterations: int = DEFAULT_MAX_ITERATIONS) -> None:`

### 54. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/orchestrator.py`
   - **Line**: 42
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, project_path: str, error_context: str = "", config: Optional[OrchestratorConfig] = None):`
   - **Suggested**: `def __init__(self, project_path: str, error_context: str = "", config: Optional[OrchestratorConfig] = None) -> None:`

### 55. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/orchestrator.py`
   - **Line**: 60
   - **Issue**: `_create_initial_state` missing return type annotation
   - **Current**: `def _create_initial_state(self, project_path: str, error_context: str) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]` for better specificity

### 56. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/orchestrator.py`
   - **Line**: 79
   - **Issue**: `start` method missing return type annotation (has it)
   - **Current**: `def start(self) -> AgentState:`
   - **Note**: Already has return type

### 57. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/orchestrator.py`
   - **Line**: 94
   - **Issue**: `_log_completion_summary` missing return type annotation
   - **Current**: `def _log_completion_summary(self, final_state: dict):`
   - **Suggested**: `def _log_completion_summary(self, final_state: dict) -> None:`

### 58. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/workflow.py`
   - **Line**: 20
   - **Issue**: `create_workflow` missing return type annotation
   - **Current**: `def create_workflow():`
   - **Suggested**: Add return type annotation (check LangGraph return type)

### 59. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/auditor.py`
   - **Line**: 12
   - **Issue**: `node_auditor` missing return type annotation
   - **Current**: `def node_auditor(state: AgentState) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]` for specificity

### 60. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/auditor.py`
   - **Line**: 59
   - **Issue**: `_check_audit_passed` missing return type annotation (has it)
   - **Current**: `def _check_audit_passed(report: str) -> bool:`
   - **Note**: Already has return type

### 61. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/fixer.py`
   - **Line**: 12
   - **Issue**: `node_fixer` missing return type annotation
   - **Current**: `def node_fixer(state: AgentState) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]`

### 62. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/judge.py`
   - **Line**: 12
   - **Issue**: `node_judge` missing return type annotation
   - **Current**: `def node_judge(state: AgentState) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]`

### 63. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/test_check.py`
   - **Line**: 14
   - **Issue**: `node_test_check` missing return type annotation
   - **Current**: `def node_test_check(state: AgentState) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]`

### 64. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/test_check.py`
   - **Line**: 46
   - **Issue**: `_handle_no_tests_found` missing return type annotation
   - **Current**: `def _handle_no_tests_found() -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, Any]`

### 65. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/nodes/test_check.py`
   - **Line**: 64
   - **Issue**: `_handle_test_result` missing return type annotation
   - **Current**: `def _handle_test_result(run_result) -> dict:`
   - **Suggested**: Add type hint for `run_result` parameter and return type

### 66. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/edges.py`
   - **Line**: 12
   - **Issue**: `should_enter_loop` missing return type annotation (has it)
   - **Current**: `def should_enter_loop(state: AgentState) -> Literal["auditor", "end"]:`
   - **Note**: Already has return type

### 67. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/edges.py`
   - **Line**: 30
   - **Issue**: `should_continue_fix` missing return type annotation (has it)
   - **Current**: `def should_continue_fix(state: AgentState) -> Literal["auditor", "end"]:`
   - **Note**: Already has return type

### 68. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/agents.py`
   - **Line**: 17
   - **Issue**: `_initialize_agents` missing return type annotation
   - **Current**: `def _initialize_agents():`
   - **Suggested**: `def _initialize_agents() -> None:`

### 69. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/agents.py`
   - **Line**: 52
   - **Issue**: `get_auditor_agent` return type uses `Optional[object]` - too generic
   - **Current**: `def get_auditor_agent() -> Optional[object]:`
   - **Suggested**: Import agent type and use specific type like `Optional[AuditorAgent]`

### 70. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/agents.py`
   - **Line**: 58
   - **Issue**: `get_fixer_agent` return type uses `Optional[object]` - too generic
   - **Current**: `def get_fixer_agent() -> Optional[object]:`
   - **Suggested**: Use specific type like `Optional[FixerAgent]`

### 71. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/agents.py`
   - **Line**: 64
   - **Issue**: `get_judge_agent` return type uses `Optional[object]` - too generic
   - **Current**: `def get_judge_agent() -> Optional[object]:`
   - **Suggested**: Use specific type like `Optional[JudgeAgent]`

### 72. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/agents.py`
   - **Line**: 70
   - **Issue**: `reset_agents` missing return type annotation
   - **Current**: `def reset_agents():`
   - **Suggested**: `def reset_agents() -> None:`

### 73. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/middleware/test_discovery.py`
   - **Line**: 34
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, project_path: str):`
   - **Suggested**: `def __init__(self, project_path: str) -> None:`

### 74. **Type Hint: Modernize tuple return type**
   - **File**: `src/orchestration/middleware/test_discovery.py`
   - **Line**: 55
   - **Issue**: Uses `tuple[Optional[str], List[str]]` - modern syntax, but should verify Python version
   - **Current**: `def _search_test_directories(self) -> tuple[Optional[str], List[str]]:`
   - **Note**: Already modern, but could use `str | None` instead of `Optional[str]` (Python 3.10+)

### 75. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/middleware/test_runner.py`
   - **Line**: 35
   - **Issue**: `__init__` missing return type annotation
   - **Current**: `def __init__(self, project_path: str, timeout: int = DEFAULT_TIMEOUT):`
   - **Suggested**: `def __init__(self, project_path: str, timeout: int = DEFAULT_TIMEOUT) -> None:`

### 76. **Type Hint: Missing return type annotation**
   - **File**: `src/orchestration/middleware/test_runner.py`
   - **Line**: 126
   - **Issue**: `_build_environment` missing return type annotation
   - **Current**: `def _build_environment(self) -> dict:`
   - **Note**: Already has return type, but could use `Dict[str, str]` for specificity

### 77. **Code Style: Remove unused import**
   - **File**: `src/tools/analysis/AnalysisTools.py`
   - **Line**: 2
   - **Issue**: `Optional` imported but not used
   - **Current**: `from typing import Optional`
   - **Suggested**: Remove unused import

### 78. **Code Style: Import organization**
   - **File**: `src/tools/analysis/AnalysisTools.py`
   - **Line**: 75-76
   - **Issue**: Imports inside method should be at top of file
   - **Current**: `import ast` and `import os` inside `_run` method
   - **Suggested**: Move to top of file

### 79. **Code Style: Inconsistent variable naming**
   - **File**: `src/tools/analysis/AnalysisTools.py`
   - **Line**: 33
   - **Issue**: Variable `ok` is not descriptive
   - **Current**: `ok = validate_path(file_path, SandboxSetup.SANDBOX_ROOT)`
   - **Suggested**: `is_valid_path = validate_path(...)`

### 80. **Docstring: Enhance docstring**
   - **File**: `main.py`
   - **Line**: 11
   - **Issue**: `main` function missing docstring
   - **Current**: No docstring
   - **Suggested**: Add docstring describing the main entry point

---

## Summary

Total items found: **80 micro-refactoring opportunities**

### Categories:
- **Type Hints**: ~45 items
- **Code Style**: ~20 items  
- **Docstrings**: ~10 items
- **Unused Imports**: ~5 items

### Priority Areas:
1. Add missing `-> None` return types to `__init__` methods
2. Modernize `Union`/`Optional` syntax to `|` operator (if Python 3.10+)
3. Modernize `Dict`/`List`/`Tuple` to lowercase (if Python 3.9+)
4. Remove unused imports
5. Fix string literal bug in `ResultAnalyzer.py` line 184
6. Translate French comments/docstrings to English
7. Enhance docstrings with proper Args/Returns sections
