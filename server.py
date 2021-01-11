import asyncio
from typing import List

from base import Base
from connection import Connection


class Server(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.clients: List[Connection] = []
        self._on_connect: callable = None
        self._on_disconnect: callable = None
        self._on_ready: callable = None

        self._current_id: int = 0

    def on_connection(self, func: callable) -> None:
        self._on_connect = func

    def on_disconnect(self, func: callable) -> None:
        self._on_disconnect = func

    def on_ready(self, func: callable) -> None:
        self._on_ready = func

    def run(self) -> None:
        self.loop.run_until_complete(self.start())

    def _get_id(self) -> None:
        self._current_id += 1
        return self._current_id - 1

    async def start(self) -> None:
        await asyncio.start_server(
            self._connect_callaback,
            self.host, self.port, loop=self.loop
        )
        await self.start_tasks()
        await self._on_ready()
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            client_copy = self.clients.copy()
            for con in client_copy:
                if not con.running:
                    self.clients.remove(con)
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
        await self._on_connect(con)
