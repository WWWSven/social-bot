import asyncio
from typing import AsyncGenerator, Set, Mapping, Dict
from fastapi import Request


class SSEManager:
    _instance = None  # 单例实例

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.connections = {}  # <str, Queue>
        return cls._instance

    async def add_connection(self, name: str, request: Request) -> AsyncGenerator[str, None]:
        if name in self.connections:
            del self.connections[name]
        queue = asyncio.Queue()
        self.connections[name] = queue
        try:
            while not await request.is_disconnected():
                data = await queue.get()
                yield data
        finally:
            del self.connections[name]

    async def send_message(self, data: str, name: str):
        if name not in self.connections:
            print(f"错误：连接 {name} 不存在")
            return  # 或抛出 HTTPException
        queue = self.connections[name]
        await queue.put(data)


    def broadcast_message(self, data: str):
        if 'broadcast' in self.connections:
            q = self.connections['broadcast']
            msg = f"event: message\ndata: {data}\n\n"
            asyncio.run(q.put(msg))
