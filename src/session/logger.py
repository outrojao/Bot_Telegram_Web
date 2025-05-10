import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.abspath(os.path.join(BASE_DIR, "../../logs/sessions_logs.json"))

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log_session(phone: str, session_name: str, prompt: str):
    logs = {}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                pass
            
    from .manager import get_session_path, get_session_hash_path
    if phone in logs:
        old_session_name = logs[phone]["session_name"]
        old_session_path = get_session_path(old_session_name)
        old_session_hash_path = get_session_hash_path(old_session_name)
        
        # Apagar os arquivos antigos se existirem
        if os.path.exists(old_session_path):
            os.remove(old_session_path)
        if os.path.exists(old_session_hash_path):
            os.remove(old_session_hash_path)

    logs[phone] = {
        "session_name": session_name,
        "prompt": prompt,
        "created_at": datetime.now().isoformat()
    }

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)
        
def get_session(phone):
    if not os.path.exists(LOG_FILE):
        return None

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    entry = logs.get(phone)
    if entry: return entry
        # return entry.get("session_name")
    return None