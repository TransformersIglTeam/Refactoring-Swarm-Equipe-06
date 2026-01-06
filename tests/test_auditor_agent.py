import sys
import types
import importlib
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# Install minimal stubs for required modules
def _install_stubs():
    # Stub for langchain_google_genai
    genai_mod = types.ModuleType("langchain_google_genai")
    class GoogleGenerativeAI:
        def __init__(self, *args, **kwargs):
            pass
    class ChatGoogleGenerativeAI:
        def __init__(self, *args, **kwargs):
            pass
    genai_mod.GoogleGenerativeAI = GoogleGenerativeAI
    genai_mod.ChatGoogleGenerativeAI = ChatGoogleGenerativeAI
    sys.modules["langchain_google_genai"] = genai_mod

    # Stub for langchain_core and submodules
    core_mod = types.ModuleType("langchain_core")
    prompts_mod = types.ModuleType("langchain_core.prompts")
    class ChatPromptTemplate:
        @classmethod
        def from_messages(cls, messages):
            return Mock()
    class SystemMessagePromptTemplate:
        @classmethod
        def from_template(cls, template):
            return Mock()
    class HumanMessagePromptTemplate:
        @classmethod
        def from_template(cls, template):
            return Mock()
    class MessagesPlaceholder:
        def __init__(self, variable_name):
            self.variable_name = variable_name
    prompts_mod.ChatPromptTemplate = ChatPromptTemplate
    prompts_mod.SystemMessagePromptTemplate = SystemMessagePromptTemplate
    prompts_mod.HumanMessagePromptTemplate = HumanMessagePromptTemplate
    prompts_mod.MessagesPlaceholder = MessagesPlaceholder
    sys.modules["langchain_core"] = core_mod
    sys.modules["langchain_core.prompts"] = prompts_mod

    # Stub for langchain.tools and agents
    tools_mod = types.ModuleType("langchain.tools")
    agents_mod = types.ModuleType("langchain.agents")
    class BaseTool:
        def __init__(self, *args, **kwargs):
            pass
    class AgentExecutor:
        def invoke(self, input_data):
            return {"output": "Mock agent response"}
    class AgentType:
        STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION = "structured_chat_zero_shot_react_description"
    def initialize_agent(*args, **kwargs):
        return Mock(spec=AgentExecutor)
    tools_mod.BaseTool = BaseTool
    agents_mod.AgentExecutor = AgentExecutor
    agents_mod.AgentType = AgentType
    agents_mod.initialize_agent = initialize_agent
    langchain_mod = types.ModuleType("langchain")
    langchain_mod.tools = tools_mod
    langchain_mod.agents = agents_mod
    sys.modules["langchain"] = langchain_mod
    sys.modules["langchain.tools"] = tools_mod
    sys.modules["langchain.agents"] = agents_mod

_install_stubs()

from src.agents.auditor.AuditorAgent import AuditorAgent
from src.agents.auditor.Models import AuditorResult, AuditResult, AuditIssue

@pytest.fixture
def mock_auditor_result():
    """Mock AuditorResult for testing."""
    audit_result = AuditResult(
        target_dir="/fake/path",
        issues_found=2,
        total_files=5,
        audit_output="Mock audit output",
        issues=[
            AuditIssue(
                file_path="test.py",
                line_number=10,
                issue_type="bug",
                severity="HIGH",
                description="Test issue",
                suggestion="Fix it"
            )
        ]
    )
    return AuditorResult(
        audit_result=audit_result,
        summary="Test summary",
        recommendations=["Fix the bugs"]
    )

@patch('src.agents.auditor.AuditorAgent.AuditorAgent._init_agent')
def test_auditor_agent_initialization(mock_init_agent, mock_auditor_result):
    """Test AuditorAgent initialization."""
    mock_init_agent.return_value = Mock()

    agent = AuditorAgent()
    assert agent.agent_name == "Auditor_Agent"
    assert agent.model_name == "gemini-2.5-flash"
    assert len(agent.tools) == 5  # ReadTool, ListItems, PylintAnalysisTool, ComplexityAnalysisTool, DocstringAnalysisTool

@patch('src.agents.auditor.AuditorAgent.AuditorAgent._init_agent')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._parse_audit_response')
def test_audit_success(mock_parse_response, mock_init_agent, mock_auditor_result):
    """Test successful audit execution."""
    mock_agent_executor = Mock()
    mock_agent_executor.invoke.return_value = {"output": "Agent analysis complete"}
    mock_init_agent.return_value = mock_agent_executor
    mock_parse_response.return_value = mock_auditor_result

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    assert result is not None
    mock_agent_executor.invoke.assert_called_once()
    mock_parse_response.assert_called_once_with("Agent analysis complete")

@patch('src.agents.auditor.AuditorAgent.AuditorAgent._init_agent')
def test_audit_agent_not_initialized(mock_init_agent):
    """Test audit when agent executor is not initialized."""
    mock_init_agent.return_value = None

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    assert result.audit_result.issues_found == 0
    assert "Agent not properly initialized" in result.summary

@patch('src.agents.auditor.AuditorAgent.AuditorAgent._init_agent')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._parse_audit_response')
def test_audit_agent_execution_fails(mock_parse_response, mock_init_agent, mock_auditor_result):
    """Test audit when agent execution fails."""
    mock_agent_executor = Mock()
    mock_agent_executor.invoke.side_effect = Exception("Agent failed")
    mock_init_agent.return_value = mock_agent_executor

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    assert "Agent failed" in result.summary
    assert result.audit_result.issues_found == 0

def test_parse_audit_response_success():
    """Test successful parsing of audit response."""
    agent = AuditorAgent()

    json_response = '''Here is my analysis:
    {
        "executive_summary": "Codebase has good structure but needs documentation",
        "critical_issues": [
            {
                "file_path": "main.py",
                "line_number": 25,
                "issue_type": "documentation",
                "severity": "MEDIUM",
                "description": "Missing docstring for main function",
                "recommendation": "Add docstring to main function"
            }
        ],
        "quality_score": "B",
        "recommendations": ["Add comprehensive docstrings", "Fix code style issues"],
        "files_analyzed": 8
    }
    '''

    result = agent._parse_audit_response(json_response)

    assert result.summary == "Codebase has good structure but needs documentation"
    assert len(result.recommendations) == 2
    assert result.audit_result.issues_found == 1
    assert result.audit_result.total_files == 8

def test_parse_audit_response_no_json():
    """Test parsing when response contains no JSON."""
    agent = AuditorAgent()

    text_response = "The code looks good overall. No major issues found."

    result = agent._parse_audit_response(text_response)

    assert result.summary == text_response
    assert result.audit_result.issues_found == 0

def test_parse_audit_response_invalid_json():
    """Test parsing when JSON is invalid."""
    agent = AuditorAgent()

    invalid_response = "Invalid { json: here"

    result = agent._parse_audit_response(invalid_response)

    assert "Failed to parse agent response" in result.summary
    assert result.audit_result.issues_found == 0

@patch('src.agents.auditor.AuditorAgent.AuditorAgent.audit')
def test_audit_and_print(mock_audit, mock_auditor_result):
    """Test audit_and_print convenience method."""
    mock_audit.return_value = mock_auditor_result

    agent = AuditorAgent()
    result = agent.audit_and_print("/fake/path")

    assert result is mock_auditor_result
    mock_audit.assert_called_once_with("/fake/path")
    sys.modules["langchain"] = langchain_mod
    sys.modules["langchain.tools"] = tools_mod

    # Stub for langchain_core.tools
    core_tools_mod = types.ModuleType("langchain_core.tools")
    core_tools_mod.BaseTool = BaseTool
    sys.modules["langchain_core.tools"] = core_tools_mod

_install_stubs()

# Ensure the repository root is on sys.path
repo_root = str(Path(__file__).resolve().parents[1])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import after stubs
from src.agents.auditor.AuditorAgent import AuditorAgent
from src.agents.auditor.Models import AuditResult, AuditStatus, AuditorResult


@pytest.fixture
def mock_audit_result():
    """Mock AuditResult for testing."""
    return AuditResult(
        status=AuditStatus.FAILED,
        issues_found=3,
        total_files=5,
        success=False,
        issues=[],
        audit_output="Mock pylint output\nMock complexity output",
        execution_time=1.5
    )


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return '{"summary": "Found 3 issues in 5 files", "recommendations": ["Fix critical bugs", "Add docstrings"]}'


@patch('src.agents.auditor.AuditorAnalyzer.AuditorAnalyzer.analyze')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._analyze_code_logic')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent.llm_call')
def test_audit_success(mock_llm_call, mock_analyze_code_logic, mock_analyze, mock_audit_result, mock_llm_response):
    """Test successful audit with LLM response."""
    mock_analyze.return_value = mock_audit_result
    mock_analyze_code_logic.return_value = []  # No additional logic issues
    mock_llm_call.return_value = mock_llm_response

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    assert isinstance(result, AuditorResult)
    assert result.summary == "Found 3 issues in 5 files"
    assert len(result.recommendations) == 2
    assert result.recommendations[0] == "Fix critical bugs"

    # Verify analyzer was called
    mock_analyze.assert_called_once_with("/fake/path")

    # Verify LLM was called with correct prompt structure
    mock_llm_call.assert_called_once()
    prompt_arg = mock_llm_call.call_args[0][0]
    assert "You are an expert Senior Code Auditor Agent" in prompt_arg
    assert "AUDIT_OUTPUT:" in prompt_arg
    assert "ISSUES_FOUND: 3" in prompt_arg
    assert "TOTAL_FILES: 5" in prompt_arg


@patch('src.agents.auditor.AuditorAnalyzer.AuditorAnalyzer.analyze')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._analyze_code_logic')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent.llm_call')
def test_audit_llm_failure_fallback(mock_llm_call, mock_analyze_code_logic, mock_analyze, mock_audit_result):
    """Test audit when LLM fails and falls back to defaults."""
    mock_analyze.return_value = mock_audit_result
    mock_analyze_code_logic.return_value = []
    mock_llm_call.return_value = None  # LLM failure

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    assert isinstance(result, AuditorResult)
    assert "Static analysis completed" in result.summary
    assert len(result.recommendations) == 1
    assert "Review the detailed issues" in result.recommendations[0]


@patch('src.agents.auditor.AuditorAnalyzer.AuditorAnalyzer.analyze')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._analyze_code_logic')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent.llm_call')
def test_audit_llm_invalid_json_fallback(mock_llm_call, mock_analyze_code_logic, mock_analyze, mock_audit_result):
    """Test audit when LLM returns invalid JSON."""
    mock_analyze.return_value = mock_audit_result
    mock_analyze_code_logic.return_value = []
    mock_llm_call.return_value = "Invalid JSON response"

    agent = AuditorAgent()
    result = agent.audit("/fake/path")

    # Should fall back to defaults
    assert "Static analysis completed" in result.summary


def test_auditor_agent_initialization():
    """Test AuditorAgent initialization."""
    agent = AuditorAgent()

    assert agent.agent_name == "Auditor_Agent"
    assert agent.model_name == "gemini-2.5-flash"
    assert hasattr(agent, 'analyzer')
    assert hasattr(agent, 'llm')


@patch('src.agents.auditor.AuditorAnalyzer.AuditorAnalyzer.analyze')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent._analyze_code_logic')
@patch('src.agents.auditor.AuditorAgent.AuditorAgent.llm_call')
def test_audit_and_print(mock_llm_call, mock_analyze_code_logic, mock_analyze, mock_audit_result, mock_llm_response, capsys):
    """Test audit_and_print method."""
    mock_analyze.return_value = mock_audit_result
    mock_analyze_code_logic.return_value = []
    mock_llm_call.return_value = mock_llm_response

    agent = AuditorAgent()
    result = agent.audit_and_print("/fake/path")

    assert isinstance(result, AuditorResult)

    # Check that print output contains expected content
    captured = capsys.readouterr()
    assert "AUDITOR ANALYSIS COMPLETE" in captured.out
    assert "Found 3 issues in 5 files" in captured.out