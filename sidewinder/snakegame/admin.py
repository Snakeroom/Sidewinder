from django.contrib import admin
from solo.admin import SingletonModelAdmin
from sidewinder.snakegame.models import SnakeGameServer


@admin.register(SnakeGameServer)
class SnakeGameServerAdmin(SingletonModelAdmin):
    pass
