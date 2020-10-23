from sidewinder.identity.models import User
from sidewinder.snakegame.models import SnakeGameServer
from channels.generic.websocket import JsonWebsocketConsumer

import threading
import random

snakes = []
joined_users = []
snakes_by_socket = {}
global_index = 0

complementary_directions = {
    0: 2,
    1: 3,
    2: 0,
    3: 1
}

def is_invalid_position(position: tuple):
    return position[0] < 0 or position[1] < 0 or position[0] >= 40 or position[1] >= 30

def has_segment_at_position(position: tuple):
    for snake in snakes:
        for segment in snake.segments:
            if segment == position:
                return True
    return False

def get_empty_position():
    position = (random.randrange(0, 40), random.randrange(0, 30))
    return get_empty_position() if has_segment_at_position(position) else position

food = get_empty_position()

def tick():
    for snake in snakes:
        snake.tick()

    global food
    if food == None:
        food = get_empty_position()

    update_packet = {
        "action": "update",
        "food": food,
        "snakes": list(map(Snake.getNetworkInfo, snakes))
    }
    for snake in snakes:
        snake.socket.send_json(update_packet)

    threading.Timer(1 / 6, tick).start()

threading.Timer(1 / 6, tick).start()

class Snake:
    def __init__(self, user: User, socket: JsonWebsocketConsumer, index: int):
        self.user = user
        self.name = user.username
        self.socket = socket
        self.index = index
        self.segments = [get_empty_position()]
        self.direction = 0
        self.previous_direction = 0

    def offset(self, position: tuple):
        # North, east, south, west
        if self.direction == 0:
            return (position[0], position[1] - 1)
        elif self.direction == 1:
            return (position[0] + 1, position[1])
        elif self.direction == 2:
            return (position[0], position[1] + 1)
        else:
            return (position[0] - 1, position[1])

    def end(self):
        self.socket.send_json({
            "action": "end",
            "score": len(self.segments) - 4
        }, close=True)

        # Cleanup
        snakes.remove(self)
        joined_users.remove(self.user.uid)
        snakes_by_socket.pop(self.socket)
    
    def tick(self):
        # End game for player if they end up in an invalid position
        next_segment = self.offset(self.segments[-1])
        if has_segment_at_position(next_segment) or is_invalid_position(next_segment):
            self.end()
            return

        self.segments.append(next_segment)

        # Handle eating food
        global food
        ate_food = next_segment == food
        if ate_food:
            food = None

        if len(self.segments) > 4 and not ate_food:
            self.segments.pop(0)

        self.previous_direction = self.direction
    
    def getNetworkInfo(self):
        return {
            "index": self.index,
            "name": self.name,
            "segments": self.segments
        }

def handle_snakegame(socket: JsonWebsocketConsumer, content: dict):
    if content["action"] == "login":
        if not "user" in socket.scope:
            return socket.send_json({
                "error": "not_authenticated"
            })
        user: User = socket.scope["user"]

        if user.uid in joined_users:
            return socket.send_json({
                "error": "already_logged_in"
            })
        elif len(snakes) >= SnakeGameServer.get_solo().max_players:
            return socket.send_json({
                "error": "too_many_players"
            })
        elif not socket in snakes_by_socket:
            global global_index
            snake = Snake(user, socket, global_index)
            global_index += 1

            snakes_by_socket[socket] = snake
            joined_users.append(user.uid)
            snakes.append(snake)

            return socket.send_json({
                "action": "login",
                "name": snake.name,
                "index": snake.index
            })
    elif not socket in snakes_by_socket:
        return socket.send_json({
            "error": "not_logged_in"
        })
    elif content["action"] == "set_direction":
        direction = max(0, min(3, content.get("direction", 0)))

        snake = snakes_by_socket[socket]
        if (direction == complementary_directions[snake.previous_direction]):
            return
        snake.direction = direction
