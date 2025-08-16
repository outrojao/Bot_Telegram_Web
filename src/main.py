from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from telethon import TelegramClient
from telethon.sessions import StringSession
import os
import asyncio
from dotenv import load_dotenv
from .session import *
from .userbot import start_userbot

load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../web/templates"))
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../web/static")), name="static")

temp_data = {}

@app.get("/", response_class=HTMLResponse)
async def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse)
async def login_existing(request: Request, phone: str = Form(...)):
    session_data = get_session(phone)
    session_path = get_session_path(
        session_data.get("session_name")
    )
    session_string = get_saved_session(phone)
    prompt = session_data.get("prompt")
    
    if not session_string:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "message": "Sessão não encontrada ou adulterada. Faça login novamente."
        })

    client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
    await client.connect()

    try:
        if await client.is_user_authorized():
            asyncio.create_task(start_userbot(client, session_path, prompt))
            return templates.TemplateResponse("login.html", {
                "request": request,
                "success_message": "Login bem-sucedido! Userbot conectado."
            })
        else:
            os.remove(session_path)
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error_message": "Sessão expirada. Por favor, faça login novamente."
            })
    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error_message": f"Erro ao conectar com a sessão existente: {e}"
        })
    finally:
        if session_path:
            encrypt_and_hash_session(session_path)
        else:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error_message": "Erro no caminho da sessão"
            })

@app.post("/send-code", response_class=HTMLResponse)
async def send_code(request: Request, phone: str = Form(...)):
    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()

    try:
        sent = await client.send_code_request(phone)

        temp_data[phone] = {
            "code_hash": sent.phone_code_hash,
            "client": client 
        }

        return templates.TemplateResponse("code.html", {
            "request": request,
            "phone": phone
        })
    except Exception as e:
         return templates.TemplateResponse("code.html", {
            "request": request,
            "error_message": f"Erro ao enviar código: {e}"
        })

@app.post("/verify", response_class=HTMLResponse)
async def verify_code(request: Request, phone: str = Form(...), code: str = Form(...)):
    data = temp_data.get(phone)
    if not data:
        return templates.TemplateResponse("code.html", {
            "request": request,
            "error_message": "Dados não encontrados. Tente novamente."
        })

    phone_code_hash = data["code_hash"]
    client = data["client"]

    try:
        await client.sign_in(phone=phone, code=code, phone_code_hash=phone_code_hash)
        
        return templates.TemplateResponse("set_bot.html", {
                    "request": request,
                    "phone": phone
                })

    except Exception as e:
        return templates.TemplateResponse("code.html", {
            "request": request,
            "error_message": f"Erro no cadastro: {e}"
        })

         
@app.post("/set_bot", response_class=HTMLResponse)
async def set_bot(request: Request, phone: str = Form(...), prompt: str = Form(...)):
    try:
        data = temp_data.get(phone)
        client = data["client"]
        session_string = client.session.save()
        session_path = None

        save_session(phone, session_string, prompt)

        session_data = get_session(phone)
        if not session_data or "session_name" not in session_data:
            print("[DEBUG] session_data inválido ou session_name ausente.")
            return templates.TemplateResponse("set_bot.html", {
                "request": request,
                "error_message": "Erro ao recuperar dados da sessão."
            })

        session_path = get_session_path(session_data["session_name"])
        print(f"[DEBUG] session_path atualizado: {session_path}")

        asyncio.create_task(start_userbot(client, session_path, prompt))
        temp_data.pop(phone, None)
        return templates.TemplateResponse("set_bot.html", {
            "request": request,
            "success_message": "Userbot conectado!"
        })
    except Exception as e:
        return templates.TemplateResponse("set_bot.html", {
            "request": request,
            "error_message": f"Erro ao iniciar bot: {e}"
        })
    finally:
        if session_path is not None:
            encrypt_and_hash_session(session_path)
        else:
            return templates.TemplateResponse("set_bot.html", {
                "request": request,
                "error_message": "Erro no caminho da sessão"
            })