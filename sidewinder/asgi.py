"""
ASGI config for sidewinder project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

from sidewinder.sneknet.routes import socket_routes

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.production')

asgi_application = get_asgi_application()

def make_django_asgi_app(scope):
    def entry_callable(receive, send):
        return asgi_application(scope, receive, send)
    return entry_callable

application = ProtocolTypeRouter({
    "http": make_django_asgi_app,
    "websocket": AuthMiddlewareStack(socket_routes)
})
