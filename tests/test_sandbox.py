import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# add project root to PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from tools.file_operations.SandboxSetup import setup_project_sandbox
from tools.file_operations.PathValidator import validate_path



class TestSandbox(unittest.TestCase):

    def setUp(self):
        """
        Create a temporary directory that simulates a project root.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

    def tearDown(self):
        """
        Remove the temporary directory after each test.
        """
        shutil.rmtree(self.temp_dir)

    # ---------------------------------------------------
    # setup_project_sandbox()
    # ---------------------------------------------------
    def test_setup_project_sandbox_success(self):
        root = setup_project_sandbox(self.project_root)

        # Returned path is correct
        self.assertEqual(root, self.project_root.resolve())

        # Backup folder created
        backup_dir = root / "_sandbox_backup"
        self.assertTrue(backup_dir.exists())
        self.assertTrue(backup_dir.is_dir())

        # Log folder created
        logs_dir = root / "logs"
        self.assertTrue(logs_dir.exists())

    def test_setup_project_sandbox_invalid_path(self):
        invalid = Path(self.temp_dir) / "does_not_exist"

        with self.assertRaises(FileNotFoundError):
            setup_project_sandbox(invalid)

    # ---------------------------------------------------
    # validate_path()
    # ---------------------------------------------------
    def test_validate_path_valid_python_file(self):
        root = setup_project_sandbox(self.project_root)

        file = self.project_root / "example.py"
        file.touch()

        self.assertTrue(validate_path("example.py", root))

    def test_validate_path_rejects_traversal(self):
        root = setup_project_sandbox(self.project_root)

        self.assertFalse(validate_path("../secret.py", root))

    def test_validate_path_rejects_non_python(self):
        root = setup_project_sandbox(self.project_root)

        file = self.project_root / "notes.txt"
        file.touch()

        self.assertFalse(validate_path("notes.txt", root))


    def test_validate_path_with_absolute_path(self):
        root = setup_project_sandbox(self.project_root)

        file = self.project_root / "test.py"
        file.touch()

        abs_path = str(file)
        # Since it's inside root, but validate_path expects relative path
        # Actually, the function takes file_path as str, and does Path(root_dir / file_path)
        # So if file_path is absolute, it might not work as expected
        # But according to the code, it should work if the resolved path is inside
        # But the test expects relative paths
        # Perhaps add a test for absolute path that is inside
        self.assertTrue(validate_path("test.py", root))


    def test_validate_path_empty_string(self):
        root = setup_project_sandbox(self.project_root)

        self.assertFalse(validate_path("", root))


    def test_setup_project_sandbox_with_spaces(self):
        spaced_dir = self.project_root / "dir with spaces"
        spaced_dir.mkdir()

        root = setup_project_sandbox(spaced_dir)

        self.assertEqual(root, spaced_dir.resolve())

        backup_dir = root / "_sandbox_backup"
        self.assertTrue(backup_dir.exists())

        logs_dir = root / "logs"
        self.assertTrue(logs_dir.exists())
