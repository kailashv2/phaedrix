from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.agents.supervisor import run
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

app = FastAPI(title="Phaedrix", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("backend/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


class ChatRequest(BaseModel):
    message: str
    session_id: str = ""


class ChatResponse(BaseModel):
    response: str
    agent: str
    session_id: str
    success: bool


@app.get("/")
def root():
    return FileResponse("backend/static/index.html")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())
    try:
        result = run(session_id, request.message)
        return ChatResponse(
            response=result["response"],
            agent=result["agent"],
            session_id=session_id,
            success=True
        )
    except Exception as e:
        return ChatResponse(
            response="Something went wrong. Please try again.",
            agent="System",
            session_id=session_id,
            success=False
        )


@app.get("/health")
def health():
    return {
        "status": "Phaedrix is running",
        "agents": ["Research Agent", "Code Agent", "Data Agent", "Utility Agent"]
    }