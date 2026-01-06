import os
import importlib
from typing import Optional, Any
from langchain_google_genai import GoogleGenerativeAI

from src.utils.logger import log_experiment, ActionType


class BaseAgent:
    """
    Minimal BaseAgent that attempts to use the Gemini Flash model via LangChain
    (guarded imports). The agent exposes a `decide` method which will use the
    model to decide whether to call tools (like the ResultAnalyzer) or act
    directly. If LangChain / Google GenAI isn't available the agent falls back
    to a deterministic heuristic.

    Note: This class deliberately keeps the LLM usage optional and non-fatal
    so unit tests and local runs without API keys still work.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", api_key_env: str = "GOOGLE_API_KEY"):
        self.model_name = model_name
        self.api_key_env = api_key_env
        self.llm = self._init_llm()

    def _init_llm(self) -> Optional[Any]:
        """Attempt to instantiate a LangChain Google GenAI LLM wrapper.
        Tries a couple of import paths and class names to be resilient across
        LangChain versions. Returns None if no supported LLM wrapper is found.
        """
        api_key = os.getenv(self.api_key_env)

        # Primary path: use explicit GoogleGenAI import from langchain-google-genai
        try:
            # Try common constructor signatures defensively
            try:
                llm = GoogleGenerativeAI(model=self.model_name, api_key=api_key)
            except TypeError:
                try:
                    llm = GoogleGenerativeAI(model=self.model_name)
                except TypeError:
                    print("Falling back to GoogleGenAI")
                        
            # Log success
            try:
                log_experiment(
                    agent_name="BaseAgent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "input_prompt": f"Instantiate langchain_google_genai.GoogleGenAI for model {self.model_name}",
                        "output_response": f"Instance created: {type(llm)}",
                    },
                    status="SUCCESS"
                )
            except Exception:
                # don't fail if logging fails
                pass

            return llm
        except Exception as e:
            try:
                log_experiment(
                    agent_name="BaseAgent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "input_prompt": f"Init LLM: attempted to load langchain_google_genai for model {self.model_name}",
                        "output_response": f"Instantiation/import failed: {repr(e)}",
                        "error": str(e)
                    },
                    status="NO_LLM"
                )
            except Exception:
                pass

        try:
            log_experiment(
                agent_name="BaseAgent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Init LLM: attempted to load LangChain Google GenAI for model {self.model_name}",
                    "output_response": "No LangChain Google GenAI LLM found. Running deterministic fallback.",
                },
                status="NO_LLM"
            )
        except Exception:
            pass

        return None

    def llm_call(self, prompt: str) -> Optional[str]:
        """Call the LLM if available and return the text response, else None."""
        if not self.llm:
            return None

        try:
            # Try a couple of common call patterns used by LangChain wrappers
            if hasattr(self.llm, "generate"):
                # some wrappers expose a `generate` method
                gen = self.llm.generate([prompt])
                # try to extract text
                text = None
                try:
                    text = gen.generations[0][0].text
                except Exception:
                    try:
                        text = str(gen)
                    except Exception:
                        text = None
                return text

            if hasattr(self.llm, "__call__"):
                return self.llm(prompt)

            # last resort: try `predict`
            if hasattr(self.llm, "predict"):
                return self.llm.predict(prompt)

        except Exception as e:
            log_experiment(
                agent_name="BaseAgent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": prompt,
                    "output_response": "LLM call raised an exception",
                    "error": str(e)
                },
                status="LLM_ERROR"
            )

        return None

    def decide(self, test_summary: str, tests_failed: int, tests_passed: int) -> str:
        """
        Decide what to do given a string summary of the test results.

        Returns one of: "ANALYZE", "PASS", "RETRY".

        If an LLM is available it'll be queried; otherwise this falls back to
        a simple heuristic (any failed tests -> ANALYZE, else PASS).
        """
        prompt = (
            "You are an automated judge using Gemini (gemini-2.5-flash).\n"
            "Given the following test summary, reply with a single keyword: ANALYZE, PASS, or RETRY.\n"
            "Only return the keyword and nothing else.\n\n"
            f"TEST_SUMMARY:\n{test_summary}\n"
            f"FAILED: {tests_failed} | PASSED: {tests_passed}\n"
        )

        # Try LLM first
        response = self.llm_call(prompt)
        if response:
            # Normalize response
            resp = response.strip().upper()
            for candidate in ("ANALYZE", "PASS", "RETRY"):
                if candidate in resp:
                    return candidate

        # Deterministic fallback
        if tests_failed > 0:
            return "ANALYZE"
        return "PASS"
