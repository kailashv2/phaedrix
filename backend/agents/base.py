from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from backend.llm import get_all_providers, build_llm
from backend.config import config
from typing import List


def run_with_fallback(messages: list, tools: list) -> str:
    last_error = None
    for provider, model in get_all_providers():
        try:
            llm = build_llm(provider, model)
            agent = create_react_agent(llm, tools)
            result = agent.invoke({"messages": messages})
            return result["messages"][-1].content
        except Exception as e:
            last_error = str(e)
            continue
    return f"All providers unavailable. Please try again. ({last_error[:80] if last_error else ''})"


def run_llm_direct(messages: list) -> str:
    last_error = None
    for provider, model in get_all_providers():
        try:
            llm = build_llm(provider, model)
            return llm.invoke(messages).content
        except Exception as e:
            last_error = str(e)
            continue
    return f"All providers unavailable. Please try again."


def trim_history(history: list) -> list:
    recent = history[-config.MAX_HISTORY:]
    trimmed = []
    for msg in recent:
        content = msg.content[:config.MAX_MSG_LENGTH] + "..." if len(msg.content) > config.MAX_MSG_LENGTH else msg.content
        trimmed.append(msg.__class__(content=content))
    return trimmed