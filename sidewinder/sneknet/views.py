from channels.generic.websocket import JsonWebsocketConsumer

from sidewinder.sneknet.models import ScienceLog


def handle_science(socket: JsonWebsocketConsumer, content):
    if "uuid" not in content or "total" not in content:
        return

    uid = content["uuid"]
    total = content["total"]

    ScienceLog.objects.update_or_create(user_hash=uid, defaults=dict(total_actions=total))
