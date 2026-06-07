from langchain_core.messages import SystemMessage, HumanMessage
from backend.agents.base import run_llm_direct
from backend.tools.code_runner import run_python_code
import re


CODE_AGENT_PROMPT = """You are the Code Agent of Phaedrix — world-class expert in every programming language and technology stack.

You can write code for ANYTHING:
- Algorithms and data structures (sorting, searching, trees, graphs, DP)
- Web apps (HTML/CSS/JS, React, Vue, Angular, Next.js)
- Backend APIs (Python/FastAPI, Node.js/Express, Java/Spring, Go, Rust)
- Full-stack applications (frontend + backend + database)
- Mobile apps (Flutter/Dart, React Native, Kotlin, Swift)
- Databases (SQL queries, MongoDB, Redis, PostgreSQL schemas)
- DevOps (Dockerfile, docker-compose, GitHub Actions, Bash scripts)
- AI/ML (PyTorch, TensorFlow, scikit-learn, LangChain)
- Games (pygame, JavaScript canvas, Unity C#)
- CLI tools, automation scripts, system programs
- Smart contracts (Solidity), Web3 apps
- Anything else — no request is too complex

RULES:
1. Write complete, production-quality, working code — never incomplete snippets
2. Use the most appropriate language/framework for the task
3. For Python: always include print() statements to demonstrate output
4. Always put code inside properly labeled ``` code blocks
5. For multi-file projects: show each file clearly with filename as header
6. For vague requests: make the most impressive smart assumption and build it fully
7. After the code: 2-3 lines on what it does and how to run it
8. Handle edge cases, follow best practices, write clean readable code
9. Never refuse a coding request — always find a way to build it"""


def _extract_language(text: str) -> str:
    match = re.search(r"```(\w+)", text)
    if match:
        lang = match.group(1).lower()
        return "python" if lang in ("python", "py") else lang
    return "unknown"


def _extract_code(text: str) -> str:
    match = re.search(r"```(?:\w+)?\n?([\s\S]*?)```", text)
    return match.group(1).strip() if match else ""


def _format_with_output(raw: str, output: str) -> str:
    match = re.search(r"```(?:\w+)?\n?([\s\S]*?)```", raw)
    if not match:
        return raw
    code = match.group(1).strip()
    lang = _extract_language(raw)
    rest = raw[match.end():].strip()
    result = f"```{lang}\n{code}\n```\n\n**Output:**\n```\n{output}\n```"
    if rest:
        result += f"\n\n{rest}"
    return result


def _is_vague(message: str) -> bool:
    words = message.lower().split()
    vague_terms = {"app", "application", "project", "something", "program", "tool", "website", "system"}
    return len(words) < 6 and any(w in vague_terms for w in words)


def run_code_agent(user_message: str, history: list) -> str:
    if _is_vague(user_message):
        prompt = (
            f"User asked: '{user_message}'\n\n"
            "This is vague. Make the smartest, most impressive assumption about what they want. "
            "State your assumption in one line, then write complete, production-quality code for it. "
            "Build something genuinely useful and impressive."
        )
    else:
        prompt = user_message

    messages = [SystemMessage(content=CODE_AGENT_PROMPT), HumanMessage(content=prompt)]
    raw = run_llm_direct(messages)
    lang = _extract_language(raw)

    if lang == "python":
        code = _extract_code(raw)
        if not code:
            return raw

        result = run_python_code.invoke({"code": code})

        if "Error:" in result:
            fix_messages = [
                SystemMessage(content=CODE_AGENT_PROMPT),
                HumanMessage(
                    content=f"Fix this Python code:\n```python\n{code}\n```\n"
                            f"Error: {result}\n"
                            "Return ONLY the corrected ```python block. No explanations."
                )
            ]
            fixed_raw = run_llm_direct(fix_messages)
            fixed_code = _extract_code(fixed_raw)
            if fixed_code:
                result = run_python_code.invoke({"code": fixed_code})
                return _format_with_output(fixed_raw, result)

        return _format_with_output(raw, result)

    return raw