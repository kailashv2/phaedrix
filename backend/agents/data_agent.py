from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import run_llm_direct
from backend.tools.code_runner import run_python_code
from backend.tools.utilities import calculate
import re


DATA_AGENT_PROMPT = """You are the Data Agent of Phaedrix — a specialized agent for data analysis, math, and calculations.

RESPONSIBILITIES:
- Perform mathematical calculations accurately
- Analyze data and provide insights
- Write Python code for data processing when needed
- Generate data visualizations using matplotlib/seaborn code
- Explain statistical concepts clearly
- Always show your work and calculations"""


def run_data_agent(user_message: str, history: list) -> str:
    messages = [
        SystemMessage(content=DATA_AGENT_PROMPT),
        HumanMessage(content=user_message)
    ]
    return run_llm_direct(messages)