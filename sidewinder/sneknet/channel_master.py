from channels.generic.websocket import JsonWebsocketConsumer

all_socket_handlers = {}

class SneknetConsumer(JsonWebsocketConsumer):
    groups = ("sneknet",)

    def receive_json(self, content, **kwargs):
        if "type" not in content:
            return

        msg_type = content["type"]

        if msg_type in all_socket_handlers:
            all_socket_handlers[msg_type](self, content)
