import asyncio
import json
from typing import Any


class Connection:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter
    ) -> None:
        self.reader = reader
        self.writer = writer

        self._recv_queue = []
        self._send_queue = []

        self.loop = loop

    def send(
        self,
        event_name: str,
        data: Any,
        event_type: str = 'event'
    ) -> None:
        self._send_queue.append(json.dumps({
            'meta': {'name': event_name, 'type': event_type},
            'data': data
        }))

    def read(self) -> Any:
        if len(self._recv_queue) == 0:
            return None
        return self._recv_queue.pop(0)

    def start(self) -> None:
        self.loop.create_task(self._main_loop())

    async def _main_loop(self) -> None:
        while True:
            print(1)
            to_send = "{}"
            if len(self._send_queue) != 0:
                to_send = self._send_queue.pop(0)

            await self._send(to_send)

            recv = await self._read()
            if recv != {}:
                self._recv_queue.append(recv)

            await asyncio.sleep(0)

    async def _send(self, to_send: str) -> None:
        self.writer.write(to_send.encode())
        await self.writer.drain()

    async def _read(self) -> Any:
        recv = await self.reader.read(100)
        return json.loads(recv)
