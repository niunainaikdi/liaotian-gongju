from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="简易聊天室")

# 存储所有连接的客户端
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """给所有连接的客户端发消息"""
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def get():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    try:
        # 通知所有人：有人加入了
        await manager.broadcast(f"系统：{username} 加入了聊天室")

        while True:
            # 接收消息
            data = await websocket.receive_text()
            time = datetime.now().strftime("%H:%M:%S")
            # 广播给所有人
            await manager.broadcast(f"[{time}] {username}：{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"系统：{username} 离开了聊天室")