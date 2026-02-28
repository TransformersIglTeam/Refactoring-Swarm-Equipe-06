"""
Dynamic prompt generation for the orchestration pipeline.
"""


class TestPrompts:
    """Prompts related to test generation and fixing."""

    NO_TESTS_FOUND = (
        "IMPORTANT: No unit tests were found in this project. "
        "You MUST generate test files in a 'tests/' directory using pytest. "
        "Every test function MUST import actual source code modules, call real functions, "
        "and contain at least one assert statement verifying output. "
        "Do NOT create placeholder tests with just 'pass' or without assertions."
    )

    TESTS_FAILING = (
        "IMPORTANT: Unit tests were found but are FAILING. "
        "Test failure output is provided below. "
        "You MUST analyze BOTH the test files AND the source code to determine "
        "where the bug is. The problem could be in the source code, in the tests, or both. "
        "Read the test files carefully and compare their expectations against "
        "the actual source code logic before writing your report.\n\n"
        "TEST FAILURE OUTPUT:\n{test_output}"
    )

    @staticmethod
    def get_no_tests_prompt() -> str:
        """Get the prompt for when no tests are found."""
        return TestPrompts.NO_TESTS_FOUND

    @staticmethod
    def get_tests_failing_prompt(test_output: str) -> str:
        """Get the prompt for when tests exist but are failing."""
        return TestPrompts.TESTS_FAILING.format(test_output=test_output[:2000])
