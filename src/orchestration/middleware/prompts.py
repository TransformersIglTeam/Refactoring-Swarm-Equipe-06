"""
Dynamic prompt generation for the orchestration pipeline.
"""


class TestPrompts:
    """Prompts related to test generation and fixing."""
    
    NO_TESTS_FOUND = (
        "IMPORTANT: No unit tests were found in this project. "
        "Before fixing any issues, you MUST first generate a 'tests' folder "
        "with appropriate test files (test_*.py) to validate the code. "
        "Create comprehensive unit tests for the existing codebase using pytest."
    )
    
    @staticmethod
    def get_no_tests_prompt() -> str:
        """Get the prompt for when no tests are found."""
        return TestPrompts.NO_TESTS_FOUND
