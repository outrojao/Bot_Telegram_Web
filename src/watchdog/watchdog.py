import asyncio
from ..session import encrypt_and_hash_session
from telethon import TelegramClient

class Watchdog:
    def __init__(self, session_path: str, timeout: int = 600, client: TelegramClient = None, verbose: bool = True):
        self.session_path = session_path
        self.timeout = timeout
        self.verbose = verbose
        self._lock = asyncio.Lock()
        self._task = None
        self.client = client

    async def _watch(self):
        try:
            await asyncio.sleep(self.timeout)
            encrypt_and_hash_session(self.session_path)
            if self.client and self.client.is_connected():
                print(f"🔌 Timeout atingido. Desconectando o bot para {self.session_path}.")
                await self.client.disconnect()
        except asyncio.CancelledError:
            if self.verbose:
                print(f"🛑 Watchdog cancelado para {self.session_path}")

    async def start(self):
        async with self._lock:
            await self._cancel_without_lock()
            self._task = asyncio.create_task(self._watch())

    async def reset(self):
        if self.verbose:
            print(f"🔄 Watchdog resetado para {self.session_path}")
        await self.start()

    async def cancel(self):
        async with self._lock:
            await self._cancel_without_lock()

    async def _cancel_without_lock(self):
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None