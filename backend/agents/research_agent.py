from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import run_with_fallback, trim_history
from backend.tools.search import get_news_search_tool, get_general_search_tool
from backend.tools.utilities import get_current_time


RESEARCH_PROMPT = """You are the Research Agent of Phaedrix — a specialized agent for finding accurate, up-to-date information.

RESPONSIBILITIES:
- Search the web for current news, events, facts, people, companies
- Always use search tools before answering — never rely on memory for current info
- Use specific search queries for better results
- Always cite sources and dates
- If first search is irrelevant, search again with different keywords
- Be concise, factual, structured"""


def run_research_agent(user_message: str, history: list) -> str:
    tools = [
        get_news_search_tool(),
        get_general_search_tool(),
        get_current_time,
    ]
    messages = [SystemMessage(content=RESEARCH_PROMPT)] + trim_history(history) + [HumanMessage(content=user_message)]
    return run_with_fallback(messages, tools)