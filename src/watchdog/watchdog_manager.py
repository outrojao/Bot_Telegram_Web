import asyncio
from .watchdog import Watchdog
from telethon import TelegramClient

class WatchdogManager:
    def __init__(self, timeout: int = 600, verbose: bool = True):
        self.watchdogs = {}
        self.timeout = timeout
        self.verbose = verbose
        self.lock = asyncio.Lock()

    async def start(self, session_path: str, client: TelegramClient = None):
        async with self.lock:
            if session_path in self.watchdogs:
                await self.watchdogs[session_path].cancel()
            self.watchdogs[session_path] = Watchdog(session_path, self.timeout, client, self.verbose)
            await self.watchdogs[session_path].start()

    async def reset(self, session_path: str):
        async with self.lock:
            if session_path in self.watchdogs:
                await self.watchdogs[session_path].reset()
            else:
                # Se não existe ainda, inicia automaticamente
                await self.start(session_path)

    async def cancel(self, session_path: str):
        async with self.lock:
            if session_path in self.watchdogs:
                await self.watchdogs[session_path].cancel()
                del self.watchdogs[session_path]

    async def cancel_all(self):
        async with self.lock:
            for session in list(self.watchdogs.keys()):
                await self.watchdogs[session].cancel()
            self.watchdogs.clear()
