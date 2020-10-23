from django.db import models
from solo.models import SingletonModel


class SnakeGameServer(SingletonModel):
    max_players = models.PositiveIntegerField(
        default=10,
        help_text='The maximum number of players that can join the snake game'
    )

    class Meta:
        verbose_name = "Snake Game Server"
        verbose_name_plural = "Snake Game Servers"

    def __str__(self):
        return f"SnakeGameServer{{max_players={self.max_players}}}"
