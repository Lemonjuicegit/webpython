from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def send(self, message: str, websocket: WebSocket):
        return await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
            
    def __getitem__(self,key):
        return self.active_connections[key]
    
    def __setitem__(self, key, value):
        if type(value) == WebSocket:
            self.active_connections[key] = value
        else:
            raise TypeError("value must be WebSocket")
    
    def __delitem__(self, key):
        del self.active_connections[key]
        
clients = ConnectionManager()