from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from backend.config import config


def get_news_search_tool():
    return TavilySearch(
        max_results=8,
        topic="news",
        days=7,
        tavily_api_key=config.TAVILY_API_KEY
    )


def get_general_search_tool():
    return TavilySearch(
        max_results=8,
        topic="general",
        tavily_api_key=config.TAVILY_API_KEY
    )