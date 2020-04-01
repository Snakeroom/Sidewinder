from channels.routing import URLRouter
from django.urls import path

from .channel_master import SneknetConsumer

socket_routes = URLRouter([
    path('', SneknetConsumer)
])
