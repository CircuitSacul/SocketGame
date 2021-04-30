import asyncio
from typing import List, Optional, Any, Callable, Awaitable

from .base import Base
from .connection import Connection


class Server(Base):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.clients: List[Connection] = []
        self._on_connect: Optional[Callable[[Connection], Awaitable[None]]] = None
        self._on_disconnect: Optional[Callable[[Connection], Awaitable[None]]] = None
        self._on_ready: Optional[Callable[[], Awaitable[None]]] = None

        self._current_id: int = 0

    def get_client(self, client_id: int) -> Optional[Connection]:
        for c in self.clients:
            if c.id == client_id:
                return c

    def send_to_all(self, event: str, data: Any) -> None:
        for c in self.clients:
            c.send(event, data)

    def on_connection(self, func: Callable[[Connection], Awaitable[None]]) -> None:
        self._on_connect = func

    def on_disconnect(self, func: Callable[[Connection], Awaitable[None]]) -> None:
        self._on_disconnect = func

    def on_ready(self, func: Callable[[], Awaitable[None]]) -> None:
        self._on_ready = func

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.stop())

    async def stop(self) -> None:
        self.stop_tasks()
        for c in self.clients:
            await c.stop()
        exit(-1)

    def _get_id(self) -> int:
        self._current_id += 1
        return self._current_id - 1

    async def start(self) -> None:
        await asyncio.start_server(
            self._connect_callaback,
            self.host, self.port, loop=self.loop
        )
        await self.start_tasks()
        if self._on_ready:
            await self._on_ready()
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            client_copy = self.clients.copy()
            for con in client_copy:
                if not con.running:
                    self.clients.remove(con)
                    if self._on_disconnect:
                        await self._on_disconnect(con)
                    continue
                recv = con.read()
                if recv is not None:
                    if recv['meta']['type'] == 'system':
                        pass
                    elif recv['meta']['type'] == 'event':
                        await self.process_event(
                            con, recv['meta']['name'],
                            recv['data']
                        )
            await asyncio.sleep(0)

    async def _connect_callaback(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        con = Connection(self.loop, reader, writer)
        con.id = self._get_id()
        con.start()
        con.send('set_id', con.id, event_type='system')
        self.clients.append(con)
        if self._on_connect:
            await self._on_connect(con)
