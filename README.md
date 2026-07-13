# Phaedrix

Multi-agent AI system with a supervisor router that classifies each message and
dispatches it to a specialized agent — Research, Code, Data, or Utility — backed
by multi-provider LLM fallback (Groq → Gemini → OpenRouter).

## Local setup

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in at least one LLM key + TAVILY_API_KEY
uvicorn backend.main:app --reload
```

Visit `http://127.0.0.1:8000`.

## Environment variables

| Variable | Required | Used for |
|---|---|---|
| `GROQ_API_KEY` | one of the three | LLM provider |
| `GEMINI_API_KEY` | one of the three | LLM provider |
| `OPENROUTER_API_KEY` | one of the three | LLM provider |
| `TAVILY_API_KEY` | yes | Research Agent web search |

At least one LLM provider key is required; more keys means more fallback resilience.

## Deploy on Render

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point at the repo — `render.yaml` configures the service automatically.
3. Set the env vars above in the Render dashboard (they're marked `sync: false` so Render will prompt for them).
4. Deploy. Health check: `GET /health`.

Note: chat history is stored as local JSON files under `backend/memory/chats/`
and the in-process session store is in memory — both reset on every redeploy
or restart. Fine for a demo; swap in a database (Postgres/Redis) if you need
persistence across deploys.
