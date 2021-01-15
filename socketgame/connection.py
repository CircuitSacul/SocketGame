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

        self.running = True

        self.id = None
        self.begins = begins

        self._loop_task = None

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

    async def stop(self) -> None:
        if self._loop_task:
            if not self._loop_task.cancelled():
                self._loop_task.cancel()
        self.writer.close()
        try:
            await self.writer.wait_closed()
        except ConnectionResetError:
            pass

    def read(self) -> Any:
        if len(self._recv_queue) == 0:
            return None
        return self._recv_queue.pop(0)

    def start(self) -> None:
        self._loop_task = self.loop.create_task(self._main_loop())

    async def _main_loop(self) -> None:
        if self.begins:
            await self._send("{}")
        while True:
            try:
                recv = await self._read()
            except ConnectionResetError:
                self.running = False
                break
            if recv != {}:
                self._recv_queue.append(recv)

            to_send = "{}"
            if len(self._send_queue) != 0:
                to_send = self._send_queue.pop(0)

            await self._send(to_send)
            await asyncio.sleep(0.001)

    async def _send(self, to_send: str) -> None:
        to_send.replace('|', '')
        to_send += '|'
        self.writer.write(to_send.encode())
        await self.writer.drain()

    async def _read(self) -> Any:
        try:
            data = (await self.reader.readuntil(b'|')).decode()
        except Exception as e:
            raise ConnectionResetError from e
        data = data[0:len(data)-1]
        return json.loads(data)
