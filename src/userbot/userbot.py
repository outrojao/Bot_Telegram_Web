from litellm import completion  # Para interagir com o modelo de IA
from collections import defaultdict  # Para armazenar mensagens por usuário
import os  # Para definir variáveis de ambiente
import asyncio  # Para gerenciar tarefas assíncronas
import time  # Para manipulação de tempo
from dotenv import load_dotenv  # Para carregar variáveis de ambiente do arquivo .env
from telethon import TelegramClient, events # Para interagir com a API do Telegram
from ..watchdog import WatchdogManager # Para gerenciar watchdogs de sessão

load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
watchdog_manager = WatchdogManager()  # Inicializa o gerenciador de watchdogs

# --- CONFIGURAÇÕES DO MODELO ---
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API_KEY")  # Chave da API do OpenRouter
MODEL = os.getenv("MODEL")  # Permite sobrescrever o modelo via variável de ambiente
AGRUPAMENTO_DELAY = 6  # segundos para agrupar mensagens

async def start_userbot(client: TelegramClient, session_path: str, prompt: str):
    asyncio.create_task(run_userbot(client, session_path, prompt))
    await watchdog_manager.start(session_path, client)  # Inicia o watchdog para a sessão

# --- FUNÇÃO PARA INICIAR O USERBOT ---
async def run_userbot(client: TelegramClient, session_path: str, prompt: str):
    # Estruturas de controle e contexto
    buffer = defaultdict(list)  # Armazena mensagens recentes para agrupamento por usuário
    history = defaultdict(list)  # Histórico completo por usuário (para contexto com a IA)
    last_message_time = {}  # Marca o último envio de mensagem por usuário
    user_locks = defaultdict(asyncio.Lock)  # Lock para evitar race condition por usuário

    # Função que processa as mensagens agrupadas
    async def process_buffer(user_id, event):
        async with user_locks[user_id]:  # Garante que uma só task por usuário execute essa lógica
            await asyncio.sleep(AGRUPAMENTO_DELAY)
            if time.time() - last_message_time[user_id] >= AGRUPAMENTO_DELAY:
                messages = " ".join(buffer[user_id]).strip()
                if not messages:
                    return

                history[user_id].append({"role": "user", "content": messages})
                context = history[user_id][-10:] # Mantém as últimas 10 mensagens no contexto

                try:
                    resposta = completion(
                        model=f'openrouter/{MODEL}',
                        messages=[
                            {
                                "role": "system",
                                "content": prompt,
                            }
                        ] + context
                    )

                    resposta_ia = resposta.choices[0].message.content.strip()
                    await event.respond(resposta_ia)
                    history[user_id].append({"role": "assistant", "content": resposta_ia})

                except Exception as e:
                    await event.respond("❌ Tive um problema ao responder. Pode tentar de novo?")

                buffer[user_id].clear()

    # Evento de mensagem recebida
    @client.on(events.NewMessage(incoming=True))
    async def handle_message(event):
        await watchdog_manager.reset(session_path)
        if not event.is_private:
            return
        
        user_id = event.sender_id
        text = event.text.strip()
        if not text:
            return  # Ignora mensagens vazias

        buffer[user_id].append(text)
        last_message_time[user_id] = time.time()

        # Dispara o processamento com delay e lock
        asyncio.create_task(process_buffer(user_id, event))

    # Inicia o userbot
    if not client.is_connected():
        await client.connect()

    await client.run_until_disconnected()
    await watchdog_manager.cancel(session_path)  # Cancela o watchdog ao desconectar