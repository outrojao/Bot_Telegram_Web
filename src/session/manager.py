import os
from dotenv import load_dotenv
import hashlib
import secrets
from cryptography.fernet import Fernet
from .logger import log_session, get_session

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../sessions"))
HASHES_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../sessions_hashes"))

os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(HASHES_DIR, exist_ok=True)

SECRET_KEY = os.getenv("SECRET_KEY").encode()
FERNET_KEY = os.getenv("FERNET_KEY").encode()
fernet = Fernet(FERNET_KEY)

def generate_safe_session_name():
    return secrets.token_hex(16)

def encrypt_and_hash_session(session_path):
    if not os.path.exists(session_path):
        print(f"[!] Arquivo {session_path} não existe. Não será criptografado.")
        return
    with open(session_path, "rb") as f:
        data = f.read()
    encrypted = fernet.encrypt(data)
    with open(session_path, "wb") as f:
        f.write(encrypted)
    save_hash(session_path)

def decrypt_session(session_path):
    with open(session_path, "rb") as f:
        data = f.read()
    decrypted = fernet.decrypt(data)
    with open(session_path, "wb") as f:
        f.write(decrypted)

def get_session_path(session_name):
    print(f"[DEBUG] Recebendo session_name: {session_name}")
    if not session_name:
        print("[DEBUG] session_name é None ou inválido.")
        return None

    if not session_name.endswith(".session"):
        session_name += ".session"
    session_path = os.path.join(SESSIONS_DIR, session_name)
    print(f"[DEBUG] Caminho da sessão gerado: {session_path}")
    return session_path

def get_session_hash_path(session_name):
    if not session_name.endswith(".session.hash"):
        session_name += ".session.hash"
    return os.path.join(HASHES_DIR, session_name)

def save_hash(session_path):
    with open(session_path, "rb") as f:
        content = f.read()
    hash_path = os.path.join(HASHES_DIR, os.path.basename(session_path) + ".hash")
    with open(hash_path, "w") as f:
        f.write(hashlib.sha256(content).hexdigest())

def verify_hash(session_path):    
    hash_path = os.path.join(HASHES_DIR, os.path.basename(session_path) + ".hash")
    if not os.path.exists(hash_path):
        return False
    with open(session_path, "rb") as f:
        content = f.read()
    with open(hash_path, "r") as f:
        saved_hash = f.read()
    return hashlib.sha256(content).hexdigest() == saved_hash

def save_session(phone: str, session_string: str, prompt: str):
    session_name = generate_safe_session_name()
    session_path = os.path.join(SESSIONS_DIR, session_name + ".session")
    with open(session_path, 'wb') as f:
        f.write(session_string.encode())
    log_session(phone, session_name, prompt)

def get_saved_session(phone: str):
    session_name = get_session(phone).get("session_name")
    if session_name:
        session_path = get_session_path(session_name)
        if os.path.exists(session_path) and verify_hash(session_path):
            decrypt_session(session_path)
            with open(session_path, 'rb') as f:
                return f.read().decode()
    return None