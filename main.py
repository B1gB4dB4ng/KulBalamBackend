import datetime
from fastapi import FastAPI, WebSocketDisconnect
from router import (
    join,
    post_likes,
    user,
    userwall,
    comment,
    group,
    group_post,
    friendship,
    images,
    order_lines,
    orders,
    product,
    reviews,
    statistics,
    test_data,
)
from db import models
from db.database import engine
from auth import authentication
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from router.client import html
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(userwall.router)
app.include_router(comment.router)
app.include_router(group.router)
app.include_router(join.router)
app.include_router(group_post.router)
app.include_router(friendship.router)
app.include_router(product.router)
app.include_router(statistics.router)
app.include_router(images.router)
app.include_router(orders.router)
app.include_router(order_lines.router)
app.include_router(test_data.router)
app.include_router(reviews.router)
app.include_router(post_likes.router)

# This enables comunication between localhost 8000 and 3000
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "Hello! Welcome to KUL-BALAM"}


class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.active_connections.append((client_id, websocket))

    def disconnect(self, websocket: WebSocket):
        self.active_connections = [
            (c_id, ws) for c_id, ws in self.active_connections if ws != websocket
        ]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for _, websocket in self.active_connections:
            await websocket.send_text(message)


manager = ConnectionManager()


@app.get("/message")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await manager.broadcast(f"[{now}] User {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await manager.broadcast(f"[{now}] User {client_id} left the chat")


# @app.on_event("startup")
# def startup_event():
#    insert_admin()


models.Base.metadata.create_all(engine)  # db engine

# app.mount('/images', StaticFiles(directory='images'), name='images')
# app.mount('/productimages', StaticFiles(directory='productimages'), name='productimages')
