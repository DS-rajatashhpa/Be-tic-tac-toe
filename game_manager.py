from fastapi import WebSocket
from models import Game

class GameManager:
    def __init__(self):
        self.active_games = {}  # Dictionary to store game_id: Game object

    class GameManager:
        def __init__(self):
            self.active_games = {}  # Dictionary to store game_id: Game object mappings

    async def connect(self, websocket: WebSocket, game_id: str):
        if game_id not in self.active_games:
            self.active_games[game_id] = Game(game_id)
        await self.active_games[game_id].add_player(
            websocket)  # 'add_player' now expects the WebSocket to be accepted

    async def process_action(self, websocket: WebSocket, game_id: str, action: str):
        game = self.active_games.get(game_id)
        if game:
            # Adjusted to pass the WebSocket object to process_move
            await game.process_move(websocket, action)


    async def disconnect(self, websocket: WebSocket, game_id: str):
        game = self.active_games.get(game_id)
        if game:
            game.remove_player(websocket)
            if game.is_empty():
                del self.active_games[game_id]