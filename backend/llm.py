from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from backend.config import config


def _build_groq(model: str) -> ChatGroq:
    return ChatGroq(
        model=model,
        temperature=0.1,
        groq_api_key=config.GROQ_API_KEY
    )


def _build_gemini() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=config.GEMINI_MODEL,
        temperature=0.1,
        google_api_key=config.GEMINI_API_KEY
    )


def _build_openrouter(model: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        temperature=0.1,
        openai_api_key=config.OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1",
    )


def get_all_providers() -> list:
    providers = []
    if config.GROQ_API_KEY:
        for m in config.GROQ_MODELS:
            providers.append(("groq", m))
    if config.GEMINI_API_KEY:
        providers.append(("gemini", None))
    if config.OPENROUTER_API_KEY:
        for m in config.OPENROUTER_MODELS:
            providers.append(("openrouter", m))
    return providers


def build_llm(provider: str, model: str):
    if provider == "groq":
        return _build_groq(model)
    elif provider == "gemini":
        return _build_gemini()
    elif provider == "openrouter":
        return _build_openrouter(model)
    raise ValueError(f"Unknown provider: {provider}")