from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from game_manager import GameManager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

manager = GameManager()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your ngrok URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str):
    await websocket.accept()
    try:
        await manager.connect(websocket, game_id)
        while True:
            data = await websocket.receive_text()
            await manager.process_action(websocket, game_id, data)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {game_id}")
    finally:
        await manager.disconnect(websocket, game_id)
