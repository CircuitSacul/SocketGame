import asyncio
from typing import List

from base import Base
from connection import Connection


class Server(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.clients: List[Connection] = []

    def run(self) -> None:
        self.loop.run_until_complete(self.start())

    async def start(self) -> None:
        await asyncio.start_server(
            self._connect_callaback,
            self.host, self.port, loop=self.loop
        )
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            for con in self.clients:
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
        con.start()
        self.clients.append(con)
