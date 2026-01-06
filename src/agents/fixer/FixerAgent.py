import os
from typing import List, Optional

from langchain.agents import AgentExecutor

from langchain_core.prompts import ChatPromptTemplate
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
    def __init__(self, model_name: str = "gemini-2.5-flash", tools: Optional[List[BaseTool]] = None):
        super().__init__(model_name=model_name)
        self.agent_name = "Fixer_Agent"
        
        # Initialize default tools
        self.tools = [
            WriteTool(),
            ReadTool(),
            ListItems()
        ]
        
        # Add any extra tools passed in
        if tools:
            self.tools.extend(tools)
            
        # Initialize LangChain Agent
        self.agent_executor = self._init_agent()

    def _init_agent(self) -> Optional[AgentExecutor]:
        if not self.llm:
            return None
            
        # Ensure we have a chat model interface for tool calling if possible
        # BaseAgent initializes GoogleGenerativeAI which is text-only usually.
        # We might need ChatGoogleGenerativeAI for tool calling.
        # For now, let's try to see if we can instantiate ChatGoogleGenerativeAI
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            api_key = os.getenv(self.api_key_env)
            chat_llm = ChatGoogleGenerativeAI(model=self.model_name, api_key=api_key, convert_system_message_to_human=True)
        except ImportError:
            # Fallback (might fail with tools)
            chat_llm = self.llm

        try:
            from langchain.agents import initialize_agent, AgentType
            
            # Note: initialize_agent with STRUCTURED_CHAT... uses its own internal prompt structure,
            # but we can pass 'prompt' to some agent types or use create_structured_chat_agent if we want full custom prompt control.
            # However, since we are forced to use the deprecated initialize_agent for compatibility,
            # we will stick to passing a custom prefix/suffix or just rely on the system message if supported.
            
            # Actually, looking at LangChain 0.1.10, create_structured_chat_agent IS available and preferred over initialize_agent
            # but the user had issues with imports. Let's stick to initialize_agent but inject our system prompt
            # into the 'agent_kwargs' which is the standard way to customize prompts in legacy agents.
            
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
                agent_kwargs={'prefix_messages': [("system", FIXER_SYSTEM_PROMPT)]} if 'chat' in self.model_name else None
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
            f"Please identify the file to fix, read it, and then overwrite it with the fixed content."
        )
        
        if self.agent_executor:
            try:
                result = self.agent_executor.invoke({"input": input_text})
                output = result.get("output", "Fix applied (agent finished).")
                
                log_experiment(
                    agent_name=self.agent_name,
                    model_used=self.model_name,
                    action=ActionType.CODE_MODIFICATION,
                    details={"input": input_text, "output": output},
                    status="SUCCESS"
                )
                return output
            except Exception as e:
                return f"Agent failed: {e}"
        else:
            return "Agent Executor not initialized (LLM issue)."
