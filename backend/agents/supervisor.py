from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from backend.agents.research_agent import run_research_agent
from backend.agents.code_agent import run_code_agent
from backend.agents.data_agent import run_data_agent
from backend.agents.base import run_llm_direct, trim_history
from backend.tools.utilities import get_weather, convert_currency, calculate, fetch_url
import re


RESEARCH_KEYWORDS = {
    "news", "latest", "current", "today", "yesterday", "recent",
    "price", "stock", "score", "who is", "what happened", "when did",
    "where is", "result", "election", "match", "exam", "update",
    "announce", "launched", "released", "died", "arrested", "won",
    "lost", "search", "find", "look up", "tell me about",
}

CODE_KEYWORDS = {
    "write code", "write a code", "write program", "write script",
    "code karo", "code banao", "fibonacci", "factorial", "palindrome",
    "linked list", "bubble sort", "merge sort", "quick sort", "binary search",
    "dynamic programming", "dfs", "bfs", "leetcode", "implement",
    "snake game", "tic tac toe", "todo app", "rest api", "flask api",
    "fastapi", "express server", "django", "react component",
    "write a function", "write a class", "python code", "java code",
    "javascript code", "cpp code", "c++ code", "golang code",
    "code of", "code for", "show me code", "write a", "create a",
    "build a", "make a", "full stack", "fullstack", "e commerce",
    "ecommerce", "web app", "mobile app", "algorithm", "data structure",
    "blockchain", "smart contract", "machine learning code",
    "neural network code", "deep learning code",
}

DATA_KEYWORDS = {
    "calculate", "compute", "math", "percentage", "average", "sum",
    "multiply", "divide", "statistics", "data analysis", "chart",
    "graph", "plot", "visualize", "dataset", "analyze",
}

UTILITY_KEYWORDS = {
    "weather", "temperature", "humidity", "convert", "usd", "inr",
    "eur", "gbp", "currency", "exchange rate", "time", "date",
    "http", "https", "www.", "link", "url", "check this", "read this",
    "analyze this link", "open this", "linkedin", "github.com",
    "summarize this", "what is on", "visit",
}

session_store: dict = {}


def _classify(message: str) -> str:
    msg = message.lower()
    if re.search(r'https?://\S+', msg):
        return "url"
    if any(kw in msg for kw in CODE_KEYWORDS):
        return "code"
    if any(kw in msg for kw in UTILITY_KEYWORDS):
        return "utility"
    if any(kw in msg for kw in DATA_KEYWORDS):
        return "data"
    if any(kw in msg for kw in RESEARCH_KEYWORDS):
        return "research"
    return "general"


def _handle_utility(message: str) -> str:
    msg = message.lower()
    if any(w in msg for w in ["weather", "temperature", "humidity", "forecast"]):
        city = message.split("in")[-1].strip() if "in" in msg else message
        return get_weather.invoke({"city": city})
    if any(w in msg for w in ["convert", "usd", "inr", "eur", "gbp", "currency", "exchange"]):
        return convert_currency.invoke({"amount_and_currencies": message})
    if any(w in msg for w in ["calculate", "compute", "%", "percent"]):
        return calculate.invoke({"expression": message})
    return None


def _handle_url(message: str, history: list) -> str:
    url_match = re.search(r'https?://\S+', message)
    if not url_match:
        return "No valid URL found in your message."
    url = url_match.group(0)
    content = fetch_url.invoke({"url": url})
    analysis_messages = [
        SystemMessage(content="You are an expert analyst. Read the page content carefully and answer the user's question about it. Be specific, accurate, and insightful."),
        HumanMessage(content=f"User request: {message}\n\nPage content:\n{content}")
    ]
    return run_llm_direct(analysis_messages)


def _general_response(message: str, history: list) -> str:
    system = SystemMessage(content="""You are Phaedrix — a world-class AI system with expertise in everything.
Answer questions accurately, concisely, and helpfully.
For factual questions use your knowledge. Be direct and structured.
Respond in the same language the user writes in.""")
    messages = [system] + trim_history(history) + [HumanMessage(content=message)]
    return run_llm_direct(messages)


def run(session_id: str, user_message: str) -> dict:
    if session_id not in session_store:
        session_store[session_id] = []

    history = session_store[session_id]
    intent = _classify(user_message)

    if intent == "url":
        agent = "Research Agent"
        response = _handle_url(user_message, history)
    elif intent == "code":
        agent = "Code Agent"
        response = run_code_agent(user_message, history)
    elif intent == "utility":
        agent = "Utility Agent"
        response = _handle_utility(user_message) or _general_response(user_message, history)
    elif intent == "data":
        agent = "Data Agent"
        response = run_data_agent(user_message, history)
    elif intent == "research":
        agent = "Research Agent"
        response = run_research_agent(user_message, history)
    else:
        agent = "Phaedrix"
        response = _general_response(user_message, history)

    session_store[session_id].append(HumanMessage(content=user_message))
    session_store[session_id].append(AIMessage(content=response))

    return {"response": response, "agent": agent}