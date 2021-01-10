import asyncio
from base import Base
from connection import Connection


class Client(Base):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.server: Connection = None

    def run(self) -> None:
        self.loop.run_until_complete(self.start())

    async def start(self) -> None:
        reader, writer = await asyncio.open_connection(
            self.host, self.port, loop=self.loop
        )
        self.server = Connection(self.loop, reader, writer)
        self.server.start()
        await self.main_loop()

    async def main_loop(self) -> None:
        while True:
            recv = self.server.read()
            if recv is not None:
                if recv['meta']['type'] == 'system':
                    pass
                elif recv['meta']['type'] == 'event':
                    await self.process_event(
                        self.server, recv['meta']['name'],
                        recv['data']
                    )

            await asyncio.sleep(0)
