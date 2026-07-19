<div align="center">

# <picture><source media="(prefers-color-scheme: dark)" srcset="logo-dark.png"><img src="logo.png" width="200" valign="middle"></picture> Phaedrix

**A multi-agent AI system with intelligent routing and automatic LLM fallback.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-agentic-1C3C3C)](https://www.langchain.com/langgraph)
[![Deployed on Render](https://img.shields.io/badge/Deployed-Render-46E3B7?logo=render&logoColor=white)](https://phaedrix.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

[**Live Demo**](https://phaedrix.onrender.com) · [Report a Bug](https://github.com/kailashv2/phaedrix/issues) · [Request a Feature](https://github.com/kailashv2/phaedrix/issues)

</div>
---

## Overview

Phaedrix is a supervisor-routed multi-agent system: every message is classified and dispatched to one of four specialized agents — **Research**, **Code**, **Data**, or **Utility** — each backed by automatic multi-provider LLM fallback (Groq → Gemini → OpenRouter), so a single provider outage or rate limit never takes the whole app down.

## Table of contents

- [How it works](#how-it-works)
- [Agents](#agents)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Environment variables](#environment-variables)
- [Running locally](#running-locally)
- [API reference](#api-reference)
- [Deployment](#deployment)
- [Known limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## How it works

Every message sent to `/chat` is classified by keyword against four categories and routed to the matching agent. If the message contains a URL, it's fetched and summarized directly, regardless of category. If nothing matches, it falls through to a general-purpose response.

```
                         User message
                              │
                              ▼
                     ┌─────────────────┐
                     │    Supervisor    │
                     │   (classifies)   │
                     └────────┬─────────┘
                              │
          ┌───────────────────┼───────────────────┬──────────────────┐
          │                   │                    │                  │
   contains a URL?     code / debug /       search / news /    calculate /
          │             script keywords      "latest" keywords   data keywords
          ▼                   ▼                    ▼                  ▼
   Fetch & summarize     Code Agent          Research Agent       Data Agent
   (detects login-
    walled pages)                                                       │
                                                              time / weather /
                                                              currency keywords
                                                                        ▼
                                                                 Utility Agent
```

Each LLM-backed agent call runs through a shared fallback layer that tries every configured provider in order until one succeeds — a rate limit on Groq, for example, transparently falls through to Gemini or OpenRouter instead of failing the request.

## Agents

| Agent | Triggers on | What it does |
|---|---|---|
| **Research Agent** | search, news, "latest", "current", people, companies | Searches the web via Tavily (news + general) and cites sources. Never answers current-events questions from memory alone. |
| **Code Agent** | write/debug/fix code, language names, "script", "function" | Writes code and executes Python in a sandboxed subset (no imports, no file or network access) to verify it runs before returning it. |
| **Data Agent** | calculate, analyze, statistics, data processing | Performs math and data analysis, writes pandas/matplotlib-style code, always shows its work. |
| **Utility Agent** | time, weather, currency conversion | Deterministic, non-LLM calls — `get_current_time`, `get_weather` (wttr.in), `convert_currency` — fast, no model call needed. |

URLs are handled as a fifth path outside this table: `fetch_url` pulls the page, detects login-walled or gated content (LinkedIn, Instagram, X, Facebook) and reports that plainly instead of asking the LLM to guess at a login wall.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn |
| Orchestration | LangChain, LangGraph (`create_react_agent`) |
| LLM providers | Groq, Google Gemini, OpenRouter — tried in order with automatic fallback |
| Search | Tavily (news + general) |
| Frontend | Single-file vanilla HTML/CSS/JS — no build step, no framework |
| Persistence | Local JSON per chat session, scoped per anonymous client ID |
| Deployment | Render (Blueprint via `render.yaml`) |

## Project structure

```
phaedrix-main/
├── backend/
│   ├── main.py              # FastAPI app, routes, CORS
│   ├── config.py            # Provider models, env var loading
│   ├── llm.py                # Provider/model construction, fallback ordering
│   ├── agents/
│   │   ├── supervisor.py     # Message classification and routing
│   │   ├── base.py           # Shared fallback + history-trimming logic
│   │   ├── research_agent.py
│   │   ├── code_agent.py
│   │   └── data_agent.py
│   ├── tools/
│   │   ├── search.py         # Tavily news/general search tools
│   │   ├── code_runner.py    # Sandboxed Python execution
│   │   └── utilities.py      # Time, weather, currency, URL fetch
│   ├── memory/
│   │   └── chat_store.py     # Per-client-scoped chat persistence
│   └── static/                # Served frontend (mirror of frontend/)
├── frontend/
│   └── index.html             # Chat UI (also copied to backend/static/)
├── requirements.txt
├── render.yaml                 # Render Blueprint config
├── Procfile
├── LICENSE
└── .env.example
```

## Getting started

### Prerequisites

- Python 3.12+
- An API key for at least one LLM provider — [Groq](https://console.groq.com/keys), [Google AI Studio](https://aistudio.google.com/apikey), or [OpenRouter](https://openrouter.ai/keys)
- A [Tavily](https://app.tavily.com) API key for search

### Installation

```bash
git clone https://github.com/kailashv2/phaedrix.git
cd phaedrix
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env            # then fill in your keys
```

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `GROQ_API_KEY` | at least one of the three below | Primary LLM provider |
| `GEMINI_API_KEY` | " | Fallback LLM provider |
| `OPENROUTER_API_KEY` | " | Fallback LLM provider |
| `TAVILY_API_KEY` | yes | Research Agent web search |

More provider keys configured means more fallback resilience — Phaedrix works with just one, but degrades gracefully if any single provider is down or rate-limited when more are set.

## Running locally

```bash
uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000`. `--reload` restarts the server automatically as you edit backend files.

## API reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the chat UI |
| `GET` | `/health` | Health check — `{"status": "Phaedrix running"}` |
| `POST` | `/chat` | Send a message. Body: `{"message": str, "session_id": str}`. Requires `X-Client-Id` header. |
| `GET` | `/chats` | List chat sessions for the requesting client. Requires `X-Client-Id` header. |
| `GET` | `/chats/{id}` | Get full message history for one chat. Requires matching `X-Client-Id`. |
| `POST` | `/chats/new` | Create a new chat session. Requires `X-Client-Id` header. |
| `DELETE` | `/chats/{id}` | Delete a chat. Requires matching `X-Client-Id`. |

The `X-Client-Id` header is a random ID the frontend generates once per browser (`localStorage`) — it scopes chat history per browser so one visitor can't see another's conversations. This is anonymous isolation, not authentication: it stops accidental cross-visitor leakage, not a determined attacker forging headers.

## Deployment

Deploys to [Render](https://render.com) via Blueprint:

1. Push to GitHub.
2. Render dashboard → **New → Blueprint** → select the repo. `render.yaml` configures the build/start commands automatically.
3. Set the four environment variables above in Render's dashboard (they're marked `sync: false`, so Render prompts for them rather than storing them in the repo).
4. Deploy. Health check: `GET /health`.

## Known limitations

- **Chat persistence is ephemeral.** History is stored as local JSON under `backend/memory/chats/`. Render's free-tier disk doesn't persist across restarts or redeploys. Fine for a demo; production would need Postgres/Redis.
- **Routing is single-agent-per-message.** The supervisor picks one category per message. A message mixing multiple intents only routes to whichever category matched first — it won't split a message across agents.
- **Client isolation, not authentication.** See the API reference note above.
- **Free-tier cold starts.** Render's free plan spins the service down after ~15 minutes idle; the first request after that takes 30–60 seconds to wake it back up.

## Roadmap

- [ ] Persistent storage (Postgres/Redis) for chat history
- [ ] Real authentication in place of anonymous client scoping
- [ ] Multi-intent messages routed across more than one agent per turn
- [ ] Streaming responses

## Contributing

Issues and pull requests are welcome. For significant changes, please open an issue first to discuss what you'd like to change.

## License

Distributed under the MIT License. See [`LICENSE`](./LICENSE) for the full text.
