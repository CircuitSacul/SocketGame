import asyncio
import typing
from typing import Dict, List, Any, Optional, Callable, Awaitable

if typing.TYPE_CHECKING:
    from .connection import Connection


class Base:
    """The base for the Server and Client classes"""
    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 65432,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.host = host
        self.port = port

        self.loop = loop or asyncio.get_event_loop()

        self.events: Dict[str, List[Callable[["Connection", Any], Awaitable[None]]]] = {}
        self.tasks: List[Callable[[], Awaitable[None]]] = []

        self._running_tasks: List[asyncio.Future[Any]] = []

    def task(self, func: Callable[[], Awaitable[None]]) -> None:
        self.tasks.append(func)

    def event(self, name: Optional[str] = None) -> Callable[[Callable[["Connection", Any], Awaitable[None]]], Callable[["Connection", Any], Awaitable[None]]]:
        def wrapper(func: Callable[["Connection", Any], Awaitable[None]]) -> Callable[["Connection", Any], Awaitable[None]]:
            event_name = name or func.__name__

            self.events.setdefault(event_name, [])
            self.events[event_name].append(func)

            return func

        return wrapper

    async def start_tasks(self) -> None:
        for func in self.tasks:
            t = self.loop.create_task(func())
            self._running_tasks.append(t)

    def stop_tasks(self) -> None:
        for t in self._running_tasks:
            if not t.cancelled():
                t.cancel()

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
