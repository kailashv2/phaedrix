import json
import os
import uuid
from datetime import datetime
from pathlib import Path

CHATS_DIR = Path(__file__).parent / "chats"
CHATS_DIR.mkdir(exist_ok=True)


def _chat_path(session_id: str) -> Path:
    return CHATS_DIR / f"{session_id}.json"


def create_session(client_id: str) -> str:
    session_id = str(uuid.uuid4())[:8]
    meta = {
        "id": session_id,
        "client_id": client_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }
    with open(_chat_path(session_id), "w") as f:
        json.dump(meta, f, indent=2)
    return session_id


def save_message(session_id: str, role: str, content: str, agent: str = None):
    path = _chat_path(session_id)
    if not path.exists():
        return

    with open(path, "r") as f:
        chat = json.load(f)

    chat["messages"].append({
        "role": role,
        "content": content,
        "agent": agent,
        "timestamp": datetime.now().isoformat()
    })
    chat["updated_at"] = datetime.now().isoformat()

    if chat["title"] == "New Chat" and role == "user":
        chat["title"] = content[:40] + ("..." if len(content) > 40 else "")

    with open(path, "w") as f:
        json.dump(chat, f, indent=2)


def get_chat(session_id: str, client_id: str) -> dict:
    path = _chat_path(session_id)
    if not path.exists():
        return None
    with open(path, "r") as f:
        chat = json.load(f)
    if chat.get("client_id") != client_id:
        return None
    return chat


def list_chats(client_id: str) -> list:
    chats = []
    for file in sorted(CHATS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True):
        with open(file, "r") as f:
            chat = json.load(f)
            if chat.get("client_id") != client_id:
                continue
            chats.append({
                "id": chat["id"],
                "title": chat["title"],
                "updated_at": chat["updated_at"],
                "message_count": len(chat["messages"])
            })
    return chats


def delete_chat(session_id: str, client_id: str) -> bool:
    path = _chat_path(session_id)
    if not path.exists():
        return False
    with open(path, "r") as f:
        chat = json.load(f)
    if chat.get("client_id") != client_id:
        return False
    path.unlink()
    return True
