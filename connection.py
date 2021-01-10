import asyncio
import json
from typing import Any


class Connection:
    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        begins: bool = False
    ) -> None:
        self.reader = reader
        self.writer = writer

        self._recv_queue = []
        self._send_queue = []

        self.loop = loop

        self.id = None
        self.begins = begins

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
        if self.begins:
            await self._send("{}")
        while True:
            recv = await self._read()
            if recv != {}:
                self._recv_queue.append(recv)

            to_send = "{}"
            if len(self._send_queue) != 0:
                to_send = self._send_queue.pop(0)

            await self._send(to_send)

    async def _send(self, to_send: str) -> None:
        to_send.replace('|', '')
        to_send += '|'
        self.writer.write(to_send.encode())
        await self.writer.drain()

    async def _read(self) -> Any:
        data = (await self.reader.readuntil(b'|')).decode()
        data = data[0:len(data)-1]
        print(data)
        return json.loads(data)
