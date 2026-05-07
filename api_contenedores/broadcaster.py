import asyncio
import json
from typing import Dict, List


class Broadcaster:
    def __init__(self):
        self._queues: Dict[int, List[asyncio.Queue]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def subscribe(self, user_id: int) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(user_id, []).append(q)
        return q

    def unsubscribe(self, user_id: int, queue: asyncio.Queue) -> None:
        queues = self._queues.get(user_id, [])
        try:
            queues.remove(queue)
        except ValueError:
            pass
        if not queues:
            self._queues.pop(user_id, None)

    def emit(self, event_type: str, data: dict, exclude_user_id: int | None = None) -> None:
        if self._loop is None:
            return
        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        for uid, queues in list(self._queues.items()):
            if uid == exclude_user_id:
                continue
            for q in list(queues):
                self._loop.call_soon_threadsafe(q.put_nowait, message)


broadcaster = Broadcaster()
