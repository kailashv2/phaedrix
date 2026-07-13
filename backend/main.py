from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from backend.agents.supervisor import run
from backend.memory.chat_store import (
    create_session, save_message, get_chat, list_chats, delete_chat
)
from dotenv import load_dotenv
import os

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
    session_id = request.session_id or create_session()
    try:
        result = run(session_id, request.message)
        save_message(session_id, "user", request.message)
        save_message(session_id, "assistant", result["response"], result["agent"])
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


@app.get("/chats")
def get_all_chats():
    return list_chats()


@app.get("/chats/{session_id}")
def get_chat_history(session_id: str):
    chat = get_chat(session_id)
    if not chat:
        return {"error": "Chat not found"}
    return chat


@app.delete("/chats/{session_id}")
def remove_chat(session_id: str):
    success = delete_chat(session_id)
    return {"success": success}


@app.post("/chats/new")
def new_chat():
    session_id = create_session()
    return {"session_id": session_id}


@app.get("/health")
def health():
    return {"status": "Phaedrix running"}