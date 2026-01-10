"""
Test discovery utilities for finding test files in a project.
"""

import os
import logging
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TestDiscoveryResult:
    """Result of test discovery."""
    tests_found: bool
    test_directory: Optional[str]
    test_files: List[str]


class TestDiscovery:
    """Discovers test files in a project."""
    
    DEFAULT_TEST_LOCATIONS = [
        "tests",
        "test",
        os.path.join("src", "tests"),
        os.path.join("src", "test"),
    ]
    
    TEST_FILE_PREFIX = "test_"
    TEST_FILE_SUFFIX = ".py"
    
    def __init__(self, project_path: str):
        self.project_path = os.path.abspath(project_path)
    
    def discover(self) -> TestDiscoveryResult:
        """
        Discover test files in the project.
        
        Returns:
            TestDiscoveryResult with discovery information.
        """
        test_dir, test_files = self._search_test_directories()
        
        if not test_files:
            test_dir, test_files = self._search_root_directory()
        
        return TestDiscoveryResult(
            tests_found=len(test_files) > 0,
            test_directory=test_dir,
            test_files=test_files
        )
    
    def _search_test_directories(self) -> tuple[Optional[str], List[str]]:
        """Search standard test directories for test files."""
        for relative_loc in self.DEFAULT_TEST_LOCATIONS:
            full_path = os.path.join(self.project_path, relative_loc)
            test_files = self._find_test_files_in_directory(full_path)
            if test_files:
                logger.debug(f"Found {len(test_files)} test files in {full_path}")
                return full_path, test_files
        return None, []
    
    def _search_root_directory(self) -> tuple[Optional[str], List[str]]:
        """Search the project root for test files."""
        test_files = self._find_test_files_in_directory(self.project_path)
        if test_files:
            logger.debug(f"Found {len(test_files)} test files in project root")
            return self.project_path, test_files
        return None, []
    
    def _find_test_files_in_directory(self, directory: str) -> List[str]:
        """Find all test files in a directory."""
        if not os.path.exists(directory) or not os.path.isdir(directory):
            return []
        
        test_files = []
        try:
            for filename in os.listdir(directory):
                if self._is_test_file(filename):
                    test_files.append(os.path.join(directory, filename))
        except PermissionError:
            logger.warning(f"Permission denied accessing {directory}")
        
        return test_files
    
    def _is_test_file(self, filename: str) -> bool:
        """Check if a filename matches the test file pattern."""
        return (
            filename.startswith(self.TEST_FILE_PREFIX) and
            filename.endswith(self.TEST_FILE_SUFFIX)
        )
