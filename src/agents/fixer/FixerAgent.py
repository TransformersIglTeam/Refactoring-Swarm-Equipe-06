import os
from typing import List, Optional

from langchain.agents import AgentExecutor

from langchain_google_genai import GoogleGenerativeAI
from langchain.tools import BaseTool

from src.agents.judge.BaseAgent import BaseAgent
from src.tools.file_operations.WriteTool import WriteTool
from src.tools.file_operations.ReadTool import ReadTool
from src.tools.file_operations.ListItems import ListItems
from src.utils import SandboxSetup
from src.utils.logger import log_experiment, ActionType

class FixerAgent(BaseAgent):
    """
    Fixer Agent responsible for applying code fixes using available tools.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash-lite", tools: Optional[List[BaseTool]] = None):
        super().__init__(model_name=model_name)
        self.agent_name = "Fixer_Agent"
        
        # Initialize default tools
        self.tools = [
            WriteTool(),
            ReadTool(),
            ListItems()
        ]
        
        if tools:
            self.tools.extend(tools)
            
        self.agent_executor = self._init_agent()

    def _init_agent(self) -> Optional[AgentExecutor]:
        if not self.llm:
            return None
            
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv(self.api_key_env)
            chat_llm = ChatGoogleGenerativeAI(model=self.model_name, api_key=api_key, convert_system_message_to_human=True)
        except ImportError:
            # Fallback (might fail with tools)
            chat_llm = self.llm

        try:
            from langchain.agents import initialize_agent, AgentType
            from src.agents.fixer.prompts import FIXER_SYSTEM_PROMPT
            
            agent_kwargs = {
                "system_message": FIXER_SYSTEM_PROMPT,
                "input_variables": ["input", "agent_scratchpad"]
            }

            return initialize_agent(
                tools=self.tools,
                llm=chat_llm,
                agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                handle_parsing_errors=True,
                agent_kwargs={"system_message": FIXER_SYSTEM_PROMPT, "prefix_messages": "you are a python engineer that specialize in python code fixing"} 
            )
        except Exception as e:
            print(f"Failed to create agent: {e}")
            return None

    def fix(self, project_path: str, analysis_result: str, judge_feedback: Optional[str] = "") -> str:
        """
        Main fix generation and application loop using tools.
        """
        # Ensure Sandbox is set (crucial for tools)
        if SandboxSetup.SANDBOX_ROOT is None:
            SandboxSetup.SANDBOX_ROOT = project_path
        
        input_text = (
            f"Fix the project at {project_path}.\n"
            f"ANALYSIS: {analysis_result}\n"
            f"FEEDBACK: {judge_feedback}\n"
            f"Please identify read the audit_report.md to know the steps to execute to fix the errors , read it, and then overwrite it with the fixed content."
        )
        
        if self.agent_executor:
            try:
                result = self.agent_executor.invoke({"input": input_text})
                output = result.get("output", "Fix applied (agent finished).")
                
                log_experiment(
                    agent_name=self.agent_name,
                    model_used=self.model_name,
                    action=ActionType.FIX,
                    details={"input_prompt": input_text, "output_response": output},
                    status="SUCCESS"
                )
                return output
            except Exception as e:
                return f"Agent failed: {e}"
        else:
            return "Agent Executor not initialized (LLM issue)."
