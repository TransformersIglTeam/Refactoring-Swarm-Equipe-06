"""
Prompts for the Judge Agent
These prompts help the Judge analyze test failures and provide feedback to the Fixer
"""

class JudgePrompts:
    """Collection of prompts for the Judge Agent"""
    
    @staticmethod
    def get_system_prompt() -> str:
        """System prompt defining the Judge's role and capabilities"""
        return """You are an expert Python testing specialist and code quality judge.

Your responsibilities:
1. Analyze pytest test results and identify the root causes of failures
2. Provide clear, actionable feedback for fixing test failures
3. Distinguish between different types of errors (syntax, logic, import, assertion)
4. Suggest specific corrections without writing complete code solutions
5. Prioritize fixes by severity and impact

Your analysis must be:
- Precise: Identify exact line numbers and error types
- Actionable: Give specific steps to fix, not vague suggestions
- Concise: Focus on the most critical issues first
- Structured: Use clear sections (Error Type, Location, Root Cause, Fix Needed)

You DO NOT write code. You analyze and guide."""

    @staticmethod
    def analyze_test_failure(
        test_output: str,
        code_content: str,
        file_path: str,
        iteration: int
    ) -> str:
        """
        Prompt for analyzing why tests failed
        
        Args:
            test_output: The pytest output showing failures
            code_content: The actual code that was tested
            file_path: Path to the file being tested
            iteration: Current iteration number in the self-healing loop
        """
        return f"""Analyze this test failure and provide actionable feedback for the Fixer agent.

**Context:**
- File: {file_path}
- Iteration: {iteration}
- This is a self-healing loop where a Fixer agent will attempt corrections based on your analysis.

**Test Output:**
```
{test_output[:2000]}  # Limit to first 2000 chars
```

**Code Being Tested:**
```python
{code_content[:1500]}  # Limit to first 1500 chars
```

**Your Task:**
Analyze the test failures and provide a structured diagnosis in the following JSON format:

{{
  "error_summary": "Brief one-line summary of the main issue",
  "error_type": "One of: SYNTAX_ERROR, IMPORT_ERROR, ASSERTION_FAILURE, RUNTIME_ERROR, LOGIC_ERROR, TYPE_ERROR",
  "severity": "One of: CRITICAL, HIGH, MEDIUM, LOW",
  "failures": [
    {{
      "test_name": "name of the failing test",
      "error_message": "the actual error message from pytest",
      "line_number": "line number where error occurred (if available)",
      "root_cause": "explanation of why this is failing",
      "fix_suggestion": "specific action the Fixer should take"
    }}
  ],
  "priority_fixes": [
    "Fix item 1: Most critical issue to address first",
    "Fix item 2: Second priority",
    "Fix item 3: Third priority"
  ],
  "code_smells_noticed": [
    "Any code quality issues that might cause future failures"
  ]
}}

**Important Guidelines:**
- If tests passed, set error_summary to "All tests passed"
- Focus on the MOST CRITICAL failures first (max 3 failures analyzed)
- Be specific about line numbers when available
- Suggest fixes that the Fixer can implement, not abstract advice
- If the same error appears multiple times, group them together

Provide ONLY the JSON response, no additional text."""

    @staticmethod
    def evaluate_code_quality(
        test_results: dict,
        pylint_score: float,
        previous_score: float
    ) -> str:
        """
        Prompt for final quality evaluation
        
        Args:
            test_results: Dict with test execution results
            pylint_score: Current pylint score
            previous_score: Pylint score before refactoring
        """
        return f"""Evaluate the overall code quality after refactoring.

**Test Results:**
- Tests Passed: {test_results.get('tests_passed', 0)}
- Tests Failed: {test_results.get('tests_failed', 0)}
- Status: {test_results.get('status', 'UNKNOWN')}

**Code Quality Metrics:**
- Current Pylint Score: {pylint_score}/10
- Previous Pylint Score: {previous_score}/10
- Improvement: {pylint_score - previous_score:+.2f} points

**Your Task:**
Provide a final quality assessment in JSON format:

{{
  "overall_verdict": "One of: EXCELLENT, GOOD, ACCEPTABLE, NEEDS_IMPROVEMENT, FAILED",
  "tests_verdict": "PASSED or FAILED with brief reason",
  "quality_verdict": "IMPROVED, MAINTAINED, or DEGRADED with brief reason",
  "remaining_issues": [
    "Issue 1 if any",
    "Issue 2 if any"
  ],
  "recommendations": [
    "Recommendation 1 for future improvements",
    "Recommendation 2"
  ],
  "ready_for_production": true or false
}}

Consider the code ready for production if:
- All tests pass (tests_passed > 0, tests_failed == 0)
- Pylint score improved OR is above 7.0
- No critical issues remain

Provide ONLY the JSON response."""

    @staticmethod
    def compare_iterations(
        current_errors: list,
        previous_errors: list,
        iteration: int
    ) -> str:
        """
        Prompt for comparing current iteration with previous
        
        Args:
            current_errors: List of errors from current iteration
            previous_errors: List of errors from previous iteration
            iteration: Current iteration number
        """
        return f"""Compare the current test results with the previous iteration to assess progress.

**Iteration:** {iteration}

**Previous Errors:**
{chr(10).join(f"- {err}" for err in previous_errors[:5])}

**Current Errors:**
{chr(10).join(f"- {err}" for err in current_errors[:5])}

**Your Task:**
Analyze whether the Fixer is making progress and provide guidance in JSON format:

{{
  "progress_status": "One of: IMPROVING, STAGNANT, REGRESSING",
  "errors_fixed": ["list of errors that were resolved"],
  "errors_introduced": ["list of new errors that appeared"],
  "errors_persisting": ["list of errors still present"],
  "next_action": "One of: CONTINUE, CHANGE_APPROACH, STOP",
  "reasoning": "Brief explanation of your assessment",
  "suggested_strategy": "Specific guidance for the next iteration if CONTINUE or CHANGE_APPROACH"
}}

**Guidelines:**
- IMPROVING: At least one error fixed, no new critical errors
- STAGNANT: Same errors persist, no progress for 2+ iterations
- REGRESSING: New errors introduced, situation worsening
- STOP: If no progress after 3+ stagnant iterations or getting worse

Provide ONLY the JSON response."""

    @staticmethod
    def extract_error_context(test_output: str, max_errors: int = 3) -> str:
        """
        Prompt for extracting the most relevant error information
        
        Args:
            test_output: Full pytest output
            max_errors: Maximum number of errors to analyze
        """
        return f"""Extract the most critical error information from this pytest output.

**Pytest Output:**
```
{test_output[:3000]}
```

**Your Task:**
Extract and structure the {max_errors} most critical errors in JSON format:

{{
  "total_failures": "number of total test failures",
  "critical_errors": [
    {{
      "test_function": "name of the test that failed",
      "error_type": "type of error (AssertionError, ImportError, etc.)",
      "error_message": "the actual error message",
      "file_location": "file:line_number if available",
      "stack_trace_snippet": "relevant 2-3 lines from stack trace",
      "failed_assertion": "what assertion failed (if applicable)"
    }}
  ],
  "common_pattern": "if multiple errors share a common cause, describe it here"
}}

**Focus on:**
- Errors that block other tests from running (imports, syntax)
- Assertion failures with clear logic issues
- Runtime errors that indicate bugs

Provide ONLY the JSON response, no additional text."""


class JudgeOutputParser:
    """Parser for Judge Agent LLM responses"""
    
    @staticmethod
    def parse_failure_analysis(llm_response: str) -> dict:
        """
        Parse the JSON response from failure analysis
        
        Args:
            llm_response: Raw LLM response
            
        Returns:
            Parsed dict or error dict
        """
        import json
        import re
        
        try:
            # Try to extract JSON from response (in case LLM adds extra text)
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Try direct parse
                return json.loads(llm_response)
                
        except json.JSONDecodeError as e:
            return {
                "error": "JSON_PARSE_ERROR",
                "message": f"Failed to parse LLM response: {str(e)}",
                "raw_response": llm_response[:500]
            }
    
    @staticmethod
    def parse_quality_evaluation(llm_response: str) -> dict:
        """Parse quality evaluation response"""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(llm_response)
        except json.JSONDecodeError:
            return {
                "overall_verdict": "PARSE_ERROR",
                "error": "Could not parse quality evaluation"
            }
    
    @staticmethod
    def parse_iteration_comparison(llm_response: str) -> dict:
        """Parse iteration comparison response"""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return json.loads(llm_response)
        except json.JSONDecodeError:
            return {
                "progress_status": "PARSE_ERROR",
                "next_action": "CONTINUE",
                "error": "Could not parse iteration comparison"
            }
    
    @staticmethod
    def extract_actionable_feedback(parsed_analysis: dict) -> str:
        """
        Convert parsed analysis into clear text feedback for the Fixer
        
        Args:
            parsed_analysis: Parsed JSON from failure analysis
            
        Returns:
            Formatted text feedback
        """
        if "error" in parsed_analysis:
            return f"Analysis Error: {parsed_analysis['message']}"
        
        feedback_lines = []
        feedback_lines.append(f"=== TEST FAILURE ANALYSIS ===")
        feedback_lines.append(f"Summary: {parsed_analysis.get('error_summary', 'Unknown error')}")
        feedback_lines.append(f"Type: {parsed_analysis.get('error_type', 'UNKNOWN')}")
        feedback_lines.append(f"Severity: {parsed_analysis.get('severity', 'UNKNOWN')}")
        feedback_lines.append("")
        
        failures = parsed_analysis.get('failures', [])
        if failures:
            feedback_lines.append("=== FAILURES DETECTED ===")
            for i, failure in enumerate(failures[:3], 1):  # Max 3 failures
                feedback_lines.append(f"\n{i}. Test: {failure.get('test_name', 'Unknown')}")
                feedback_lines.append(f"   Error: {failure.get('error_message', 'No message')}")
                if failure.get('line_number'):
                    feedback_lines.append(f"   Location: Line {failure['line_number']}")
                feedback_lines.append(f"   Root Cause: {failure.get('root_cause', 'Unknown')}")
                feedback_lines.append(f"   Fix Needed: {failure.get('fix_suggestion', 'No suggestion')}")
        
        priority_fixes = parsed_analysis.get('priority_fixes', [])
        if priority_fixes:
            feedback_lines.append("\n=== PRIORITY FIXES (IN ORDER) ===")
            for i, fix in enumerate(priority_fixes, 1):
                feedback_lines.append(f"{i}. {fix}")
        
        code_smells = parsed_analysis.get('code_smells_noticed', [])
        if code_smells:
            feedback_lines.append("\n=== CODE QUALITY ISSUES ===")
            for smell in code_smells:
                feedback_lines.append(f"- {smell}")
        
        return "\n".join(feedback_lines)