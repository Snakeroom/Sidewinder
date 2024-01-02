from channels.generic.websocket import JsonWebsocketConsumer
from django.http import HttpRequest, JsonResponse

from sidewinder.sneknet.models import ScienceLog, Token, UserScript

def handle_science(socket: JsonWebsocketConsumer, content):
    if "uuid" not in content or "total" not in content:
        return

    uid = content["uuid"]
    total = content["total"]

    ScienceLog.objects.update_or_create(user_hash=uid, defaults=dict(total_actions=total))

def get_owned_tokens(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Not signed in.", 'code': 'not_authenticated'
        }, status=401)

    tokens = [{
        "name": token.friendly_name,
        "active": token.active,
        "whitelisted_address": token.whitelisted_address,
        "truncated_value": token.token[:6],
    } for token in Token.objects.filter(owner=request.user)]

    return JsonResponse({
        "tokens": tokens,
    }, status=200)

def get_user_scripts(request: HttpRequest):
    if not request.user.is_authenticated:
        return JsonResponse({
            "error": "Not signed in.", 'code': 'not_authenticated'
        }, status=401)

    scripts = [{
        "name": script.name,
        "description": script.description,
        "location": script.location,
        "version": script.version,
        "recommended": script.recommended,
        "force_disable": script.force_disable,
    } for script in UserScript.objects.all()]

    return JsonResponse({
        "scripts": scripts,
    }, status=200)
