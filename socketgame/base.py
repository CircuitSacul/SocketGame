import asyncio
from typing import Dict, List, Any


class Base:
    """The base for the Server and Client classes"""
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 65432,
        loop: asyncio.AbstractEventLoop = None
    ) -> None:
        self.host = host
        self.port = port

        self.loop = loop or asyncio.get_event_loop()

        self.events: Dict[str, callable] = {}
        self.tasks: List[callable] = []

    def task(self, func: callable) -> None:
        self.tasks.append(func)

    def event(self, name: str = None) -> callable:
        def wrapper(func: callable) -> callable:
            event_name = name or func.__name__

            self.events.setdefault(event_name, [])
            self.events[event_name].append(func)

            return func

        return wrapper

    async def start_tasks(self) -> None:
        for func in self.tasks:
            self.loop.create_task(func())

    async def process_event(
        self,
        con: Any,
        name: str,
        data: Any
    ) -> None:
        if name not in self.events:
            return

        for func in self.events[name]:
            try:
                await func(con, data)
            except Exception as e:
                print(type(e), e)
