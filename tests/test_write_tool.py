import sys
import types
import importlib
from pathlib import Path
import pytest

# Minimal stub for langchain.tools.BaseTool to avoid installing langchain in tests
def _install_langchain_stub():
    tools_mod = types.ModuleType("langchain.tools")
    class BaseTool:
        def __init__(self, *args, **kwargs):
            pass
    tools_mod.BaseTool = BaseTool

    langchain_mod = types.ModuleType("langchain")
    langchain_mod.tools = tools_mod

    sys.modules["langchain"] = langchain_mod
    sys.modules["langchain.tools"] = tools_mod


_install_langchain_stub()

# Ensure repo root is importable as `src`
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

WriteTool = importlib.import_module("src.tools.file_operations.WriteTool").WriteTool
SandboxSetup = importlib.import_module("src.tools.file_operations.SandboxSetup")
setup_project_sandbox = SandboxSetup.setup_project_sandbox


def make_writer(**overrides):
    """Helper to construct a WriteTool instance and apply attribute overrides."""
    wt = WriteTool(create_backup=overrides.get("create_backup", True))
    # Set sensible defaults for missing attributes used by the implementation
    wt.max_file_size = overrides.get("max_file_size", 10 * 1024 * 1024)  # 10 MB
    wt.validate_python = overrides.get("validate_python", False)

    # Attach optional _validate_python_syntax stub
    if "_validate_python_syntax" in overrides:
        wt._validate_python_syntax = types.MethodType(overrides["_validate_python_syntax"], wt)

    # Attach optional _write_atomically stub
    if "_write_atomically" in overrides:
        wt._write_atomically = types.MethodType(overrides["_write_atomically"], wt)

    return wt


def test_write_success(tmp_path):
    out = tmp_path / "out.py"
    content = "hello write"
    setup_project_sandbox(tmp_path)

    def _write_atomically(self, path, content_arg):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            f.write(content_arg)
        return True, ""

    wt = make_writer(create_backup=False, _write_atomically=_write_atomically)
    res = wt._run(out.name, content)

    assert "Success: Wrote" in res
    assert out.read_text(encoding="utf-8") == content


def test_backup_created(tmp_path):
    out = tmp_path / "code.py"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("old", encoding="utf-8")

    new_content = "print('new')\n"

    def _write_atomically(self, path, content_arg):
        with path.open("w", encoding="utf-8") as f:
            f.write(content_arg)
        return True, ""

    setup_project_sandbox(tmp_path)
    wt = make_writer(create_backup=True, _write_atomically=_write_atomically)
    res = wt._run(out.name, new_content)

    # Expect success and a backup mention
    assert "Success: Wrote" in res
    assert "Backup created" in res or "Backup failed" not in res

    # Ensure original content has been replaced
    assert out.read_text(encoding="utf-8") == new_content


def test_permission_error_writing(tmp_path):
    out = tmp_path / "nope.py"
    content = "data"

    def _write_atomically(self, path, content_arg):
        raise PermissionError("no write")

    setup_project_sandbox(tmp_path)
    wt = make_writer(_write_atomically=_write_atomically)
    res = wt._run(out.name, content)
    assert "Permission denied" in res


def test_content_too_large(tmp_path):
    out = tmp_path / "big.py"
    content = "x" * 1024  # 1 KB
    setup_project_sandbox(tmp_path)

    wt = make_writer(max_file_size=10)  # tiny max to trigger
    res = wt._run(out.name, content)
    assert "Error: Content too large" in res


def test_invalid_python_syntax(tmp_path):
    out = tmp_path / "bad.py"
    content = "def f(:\n    pass"
    setup_project_sandbox(tmp_path)
    def _validate_python_syntax(self, content_arg):
        # simulate detection of invalid syntax
        return False, "unexpected EOF"

    wt = make_writer(validate_python=True, _validate_python_syntax=_validate_python_syntax)
    res = wt._run(out.name, content)
    assert "Invalid Python syntax" in res
