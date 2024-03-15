import json

from fastapi import WebSocket

class Game:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players = []  # This will hold WebSocket instances
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.current_turn = "X"
        self.winner = None
        self.game_started = False

    async def add_player(self, websocket):
        symbol = "X" if len(self.players) == 0 else "O"
        self.players.append((websocket, symbol))
        await websocket.send_text(json.dumps({"status": "assignSymbol", "symbol": symbol}))

        if len(self.players) == 2:
            await self.broadcast({"status": "start", "currentTurn": self.current_turn})

    async def broadcast(self, message: dict):
        # Convert the message dictionary to a JSON string
        message_json = json.dumps(message)
        print(message)
        for player_websocket, _ in self.players:
            await player_websocket.send_text(message_json)

    def is_empty(self):
        return not self.players

    async def process_move(self, websocket: WebSocket,  action: str):
        # Deserialize the action from string to dictionary
        move = json.loads(action)
        symbol = move.get("symbol")
        row = move.get("row")
        col = move.get("column")
        # Validate the move
        if symbol != self.current_turn or self.board[row][col] != '' or self.winner is not None:
            await self.send_direct_message(websocket, {"status": "error", "reason": "Invalid move"})
            return

        # Make the move
        self.board[row][col] = symbol
        print('pass')
        # Check for win or draw
        if self.check_win(symbol):
            self.winner = symbol
            await self.broadcast({"status": "win", "player": symbol, "board": self.board})
        elif self.check_draw():
            await self.broadcast({"status": "draw", "board": self.board})
        else:
            # Toggle the turn to the other player
            self.current_turn = "O" if symbol == "X" else "X"
            await self.broadcast({"status": "continue", "next_player": self.current_turn, "board": self.board})

    def check_win(self, symbol):
        # Check rows, columns, and diagonals for a win
        win_conditions = [
            [self.board[i][0] == symbol and self.board[i][1] == symbol and self.board[i][2] == symbol for i in
             range(3)],  # Rows
            [self.board[0][i] == symbol and self.board[1][i] == symbol and self.board[2][i] == symbol for i in
             range(3)],  # Columns
            [self.board[0][0] == symbol and self.board[1][1] == symbol and self.board[2][2] == symbol],
            # Diagonal top-left to bottom-right
            [self.board[0][2] == symbol and self.board[1][1] == symbol and self.board[2][0] == symbol]
            # Diagonal top-right to bottom-left
        ]
        return any(any(row) for row in win_conditions)

    def check_draw(self):
        return all(self.board[row][col] != "" for row in range(3) for col in range(3))

    def remove_player(self, websocket: WebSocket):
        # Filter out the player to remove based on the websocket object
        self.players = [player for player in self.players if player[0] != websocket]

    async def send_direct_message(self, websocket: WebSocket, message: dict):
        # Convert the message dictionary to a JSON string
        message_json = json.dumps(message)
        await websocket.send_text(message_json)
