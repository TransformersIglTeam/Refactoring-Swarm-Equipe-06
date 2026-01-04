import sys
import types
import importlib
import asyncio
from pathlib import Path

# Use pytest for assertions and tmp_path fixture
import pytest

# Stub langchain.tools.BaseTool to avoid requiring the real package
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

ListItems = importlib.import_module("src.tools.file_operations.ListItems").ListItems


def test_list_items_happy(tmp_path):
    # create files and a dir in tmp_path
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "d").mkdir()

    tool = ListItems()
    res = tool._run(str(tmp_path))

    # split lines and compare sorted entries
    lines = res.splitlines()
    expected = sorted([p.name for p in tmp_path.iterdir()])
    assert lines == expected


def test_list_items_nonexistent(tmp_path):
    missing = tmp_path / "no_such_dir"
    tool = ListItems()
    res = tool._run(str(missing))
    assert res.startswith("Error listing directory:")


def test_arun_matches_run(tmp_path):
    (tmp_path / "file.txt").write_text("x")
    tool = ListItems()
    sync = tool._run(str(tmp_path))
    async_res = asyncio.run(tool._arun(str(tmp_path)))
    assert async_res == sync


def test_permission_error(tmp_path):
    p = tmp_path / "protected"
    p.mkdir()
    (p / "inside.txt").write_text("secret")

    # remove permissions so iterdir should raise
    p.chmod(0o000)
    try:
        tool = ListItems()
        res = tool._run(str(p))
        assert res.startswith("Error listing directory:")
    finally:
        # restore so pytest can cleanup
        p.chmod(0o755)
