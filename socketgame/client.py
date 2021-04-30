import asyncio
from typing import Any, Callable, Awaitable, Optional

from .base import Base
from .connection import Connection


class Client(Base):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.server: Optional[Connection] = None
        self.id: Optional[int] = None

        self._on_ready: Optional[Callable[[], Awaitable[None]]] = None

    def send(self, event: str, data: Any) -> None:
        if self.server is None:
            raise Exception("Server is None.")
        self.server.send(event, data)

    def run(self) -> None:
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            pass
        finally:
            self.loop.run_until_complete(self.stop())

    async def start(self) -> None:
        reader, writer = await asyncio.open_connection(
            self.host, self.port, loop=self.loop
        )
        self.server = Connection(self.loop, reader, writer, begins=True)
        self.server.start()
        await self.start_tasks()
        if self._on_ready:
            await self._on_ready()
        await self.main_loop()

    async def stop(self) -> None:
        self.stop_tasks()
        if self.server is not None:
            await self.server.stop()
        exit(-1)

    async def main_loop(self) -> None:
        if self.server is None:
            raise Exception("Server is None.")
        while True:
            if not self.server.running:
                break
            recv = self.server.read()
            if recv is not None:
                if recv['meta']['type'] == 'system':
                    if recv['meta']['name'] == 'set_id':
                        self.id = int(recv['data'])
                elif recv['meta']['type'] == 'event':
                    await self.process_event(
                        self.server, recv['meta']['name'],
                        recv['data']
                    )

            await asyncio.sleep(0)
