import re
from typing import List, Dict, Tuple


class TestParser:
    """Parses pytest output to extract test statistics and errors"""
    
    @staticmethod
    def parse_summary(output: str) -> Tuple[int, int, int]:
        """
        Extract test counts from pytest summary
        
        Args:
            output: Pytest stdout
            
        Returns:
            Tuple of (passed, failed, total)
        """
        passed = 0
        failed = 0

        # Look for common summary lines like: "5 passed, 2 failed in 1.23s" or "= 5 passed, 2 failed in 1.23s ="
        # We'll search for all occurrences and sum when appropriate.
        passed_pattern = r"(\d+)\s+passed"
        failed_pattern = r"(\d+)\s+failed"

        passed_matches = re.findall(passed_pattern, output, re.IGNORECASE)
        failed_matches = re.findall(failed_pattern, output, re.IGNORECASE)

        if passed_matches:
            # take the last occurrence (summary line usually appears near the end)
            passed = int(passed_matches[-1])

        if failed_matches:
            failed = int(failed_matches[-1])

        total = passed + failed
        return passed, failed, total
    
    @staticmethod
    def extract_errors(output: str) -> List[str]:
        """
        Extract error messages from pytest output
        
        Args:
            output: Pytest stdout
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Pattern for FAILED lines
        failed_pattern = r'FAILED\s+([^\s]+)\s+-\s+(.+?)(?:\n|$)'
        matches = re.findall(failed_pattern, output)
        
        for test_name, error in matches:
            errors.append(f"{test_name}: {error.strip()}")
        
        # If no matches, try to extract from ERROR section
        if not errors:
            error_section_pattern = r'ERROR\s+([^\n]+)'
            error_matches = re.findall(error_section_pattern, output)
            errors.extend(error_matches)
        
        return errors[:5]  # Return max 5 errors
    
    @staticmethod
    def extract_failure_details(output: str) -> List[Dict[str, str]]:
        """
        Extract detailed failure information
        
        Args:
            output: Pytest stdout
            
        Returns:
            List of dicts with failure details
        """
        failures = []

        # Pytest separates failure sections with long underscore lines. Split
        # on lines that contain at least 2 underscores to get candidate sections.
        sections = re.split(r"\n_{2,}.*\n", output)

        for section in sections:
            # Heuristic: consider sections that mention a test path::name or contain 'FAILED'/'ERROR' or 'E   '
            if ('FAILED' in section) or ('ERROR' in section) or ("::" in section and "test" in section) or ("E   " in section):
                failure = TestParser._parse_failure_section(section)
                if failure:
                    failures.append(failure)

        return failures[:3]  # Max 3 detailed failures
    
    @staticmethod
    def _parse_failure_section(section: str) -> Dict[str, str]:
        """Parse a single failure section"""
        failure = {}
        
        # Extract test name: look for patterns like path/to/file.py::test_name
        test_match = re.search(r'([\w\./\\-]+\.py::[A-Za-z0-9_]+)', section)
        if test_match:
            failure['test_name'] = test_match.group(1)
        else:
            # fallback: any token with ::
            test_match = re.search(r'([^\s:]+::[^\s:]+)', section)
            if test_match:
                failure['test_name'] = test_match.group(1)

        # Extract error type from common Python exceptions
        error_type_match = re.search(r'(AssertionError|TypeError|ValueError|ZeroDivisionError|ImportError|AttributeError|KeyError|IndexError)', section)
        if error_type_match:
            failure['error_type'] = error_type_match.group(1)
        else:
            failure['error_type'] = 'Unknown'

        # Try to extract the error message. Pytest usually prefixes traceback lines with 'E   '
        error_lines = []
        for line in section.split('\n'):
            if line.strip().startswith('E') or line.strip().startswith('>'):
                # strip leading 'E   ' or '> '
                cleaned = re.sub(r'^E\s+', '', line).strip()
                cleaned = re.sub(r'^>\s+', '', cleaned).strip()
                if cleaned:
                    error_lines.append(cleaned)

        # If we found explicit error lines, join them into a message
        if error_lines:
            failure['error_message'] = ' '.join(error_lines[:4])
        else:
            # As a final fallback, try to capture the line after the error type
            lines = section.split('\n')
            found = False
            for i, line in enumerate(lines):
                if failure.get('error_type') in line and i + 1 < len(lines):
                    failure['error_message'] = lines[i + 1].strip()
                    found = True
                    break
            if not found:
                # Try to find any non-empty short line that looks like a message
                for line in lines:
                    s = line.strip()
                    if s and len(s) < 400 and 'def ' not in s and s.startswith('(') is False:
                        failure['error_message'] = s
                        found = True
                        break
            if not found:
                failure['error_message'] = 'No detailed message available'

        return failure if 'test_name' in failure else {}