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
    return position[0] < 0 or position[1] < 0 or position[0] >= SnakeGameServer.get_solo().arena_width or position[1] >= SnakeGameServer.get_solo().arena_height

def has_segment_at_position(position: tuple):
    for snake in snakes:
        for segment in snake.segments:
            if segment == position:
                return True
    return False

def is_position_occupied(position: tuple):
    if has_segment_at_position(position):
        return True
    for food in foods:
        if food == position:
            return True
    return False

def get_empty_position():
    position = (random.randrange(0, SnakeGameServer.get_solo().arena_width), random.randrange(0, SnakeGameServer.get_solo().arena_height))
    return get_empty_position() if is_position_occupied(position) else position

foods = []

def tick():
    for snake in snakes:
        snake.tick()

    if len(foods) < SnakeGameServer.get_solo().food_amount:
        foods.append(get_empty_position())

    update_packet = {
        "action": "update",
        "food": foods[0],
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
        self.score = 0
        self.segments = [get_empty_position()]
        self.segments_to_add = SnakeGameServer.get_solo().initial_segments
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
            "score": self.score
        }, close=True)

        # Cleanup
        snakes.remove(self)
        joined_users.remove(self.user.uid)
        snakes_by_socket.pop(self.socket)
    
    def can_add_segment(self):
        if SnakeGameServer.get_solo().max_segments == None:
            return True
        return len(self.segments) <= SnakeGameServer.get_solo().max_segments
    
    def tick(self):
        # End game for player if they end up in an invalid position
        next_segment = self.offset(self.segments[-1])
        if has_segment_at_position(next_segment) or is_invalid_position(next_segment):
            self.end()
            return

        self.segments.append(next_segment)

        # Handle eating food
        for food in foods:
            if next_segment == food:
                self.score += SnakeGameServer.get_solo().food_score
                self.segments_to_add += SnakeGameServer.get_solo().food_score
                foods.remove(food)

        if self.segments_to_add > 0 and self.can_add_segment():
            self.segments_to_add -= 1
        else:
            self.segments.pop(0)

        self.previous_direction = self.direction
    
    def getNetworkInfo(self):
        return {
            "index": self.index,
            "name": self.name,
            "segments": self.segments,
            "score": self.score
        }

def handle_snakegame(socket: JsonWebsocketConsumer, content: dict):
    if content["action"] == "login":
        if not "user" in socket.scope:
            return socket.send_json({
                "error": "not_authenticated",
                "message": "You must be authenticated"
            }, close=True)
        user: User = socket.scope["user"]

        if user.uid in joined_users:
            return socket.send_json({
                "error": "already_logged_in",
                "message": "You are already logged in!"
            }, close=True)
        elif len(snakes) >= SnakeGameServer.get_solo().max_players:
            return socket.send_json({
                "error": "too_many_players",
                "message": f"Too many players (maximum: {SnakeGameServer.get_solo().max_players})"
            }, close=True)
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
            "error": "not_logged_in",
            "message": "You must be logged in to perform actions"
        }, close=True)
    elif content["action"] == "set_direction":
        direction = max(0, min(3, content.get("direction", 0)))

        snake = snakes_by_socket[socket]
        if (direction == complementary_directions[snake.previous_direction]):
            return
        snake.direction = direction
