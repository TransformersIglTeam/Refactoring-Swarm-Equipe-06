import sys
import types
import importlib
import asyncio
import pytest
from pathlib import Path

# Install a minimal stub for langchain.tools.BaseTool so tests don't require the real package.
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

# Ensure the repository root is on sys.path so `src` is importable during tests
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import the ReadTool now that the stub is in place
ReadTool = importlib.import_module("src.tools.file_operations.ReadTool").ReadTool

# Import sandbox setup after sys.path has been fixed
SandboxSetup = importlib.import_module("src.tools.file_operations.SandboxSetup")
setup_project_sandbox = SandboxSetup.setup_project_sandbox


def test_read_existing(tmp_path):
    p = tmp_path / "sample.py"
    p.write_text("hello world", encoding="utf-8")
    # initialize sandbox to tmp_path
    setup_project_sandbox(tmp_path)
    rt = ReadTool()
    assert rt._run("sample.py") == "hello world"


def test_read_nonexistent(tmp_path):
    setup_project_sandbox(tmp_path)
    rt = ReadTool()
    res = rt._run("nope.py")
    assert "does not exist" in res or "Unsafe or invalid" in res


def test_read_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    setup_project_sandbox(tmp_path)
    rt = ReadTool()
    res = rt._run("d")
    # directory is not a file, expect error
    assert "Error" in res


def test_arun_returns_same(tmp_path):
    p = tmp_path / "async.py"
    p.write_text("async content", encoding="utf-8")
    setup_project_sandbox(tmp_path)
    rt = ReadTool()
    # run the coroutine explicitly to avoid depending on pytest-asyncio
    res = asyncio.run(rt._arun("async.py"))
    assert res == "async content"


def test_permission_error(tmp_path):
    # Create a file and remove read permission to trigger an error on open
    p = tmp_path / "no_read.py"
    p.write_text("secret", encoding="utf-8")
    # remove all permissions for owner/group/others
    p.chmod(0o000)
    try:
        setup_project_sandbox(tmp_path)
        rt = ReadTool()
        res = rt._run("no_read.py")
        # On permission error the implementation returns an "Error reading file" message
        assert "Error reading file" in res
    finally:
        # restore permissions so pytest can cleanup the tmp_path
        p.chmod(0o644)
