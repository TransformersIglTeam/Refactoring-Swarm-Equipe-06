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

# Import the WriteTool now that the stub is in place
WriteTool = importlib.import_module("src.tools.file_operations.WriteTool").WriteTool


def test_write_new_file(tmp_path):
    p = tmp_path / "new_file.txt"
    wt = WriteTool()
    result = wt._run(str(p), "hello world")
    assert "Successfully wrote" in result
    assert p.read_text(encoding="utf-8") == "hello world"


def test_write_overwrite_existing(tmp_path):
    p = tmp_path / "existing.txt"
    p.write_text("old content", encoding="utf-8")
    wt = WriteTool()
    result = wt._run(str(p), "new content")
    assert "Successfully wrote" in result
    assert p.read_text(encoding="utf-8") == "new content"


def test_write_to_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    wt = WriteTool()
    res = wt._run(str(d), "some content")
    assert "Path is a directory" in res


def test_write_parent_not_exist(tmp_path):
    missing_dir = tmp_path / "nonexistent_dir" / "file.txt"
    wt = WriteTool()
    res = wt._run(str(missing_dir), "content")
    assert "parent directory" in res and "does not exist" in res


def test_arun_returns_same(tmp_path):
    p = tmp_path / "async_write.txt"
    wt = WriteTool()
    # run the coroutine explicitly to avoid depending on pytest-asyncio
    res = asyncio.run(wt._arun(str(p), "async content"))
    assert "Successfully wrote" in res
    assert p.read_text(encoding="utf-8") == "async content"


def test_permission_error(tmp_path):
    # Create a file and remove write permission to trigger an error on open
    p = tmp_path / "no_write.txt"
    p.write_text("initial", encoding="utf-8")
    # remove all permissions for owner/group/others
    p.chmod(0o000)
    try:
        wt = WriteTool()
        res = wt._run(str(p), "new content")
        # On permission error the implementation returns an "Error writing file" message
        assert "Error writing file" in res
    finally:
        # restore permissions so pytest can cleanup the tmp_path
        p.chmod(0o644)
