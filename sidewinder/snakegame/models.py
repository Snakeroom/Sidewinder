from django.db import models
from solo.models import SingletonModel


class SnakeGameServer(SingletonModel):
    max_players = models.PositiveIntegerField(
        verbose_name='Maximum Players',
        default=10,
        help_text='The maximum number of players that can join the snake game'
    )
    arena_width = models.PositiveIntegerField(
        verbose_name='Arena Width',
        default=40,
        help_text='The width of the arena'
    )
    arena_height = models.PositiveIntegerField(
        verbose_name='Arena Height',
        default=30,
        help_text='The height of the arena'
    )
    food_amount = models.PositiveIntegerField(
        verbose_name='Food Amount',
        default=1,
        help_text='The amount of food to keep on screen at any given time'
    )
    food_score = models.PositiveIntegerField(
        verbose_name='Food Score',
        default=1,
        help_text='The score and amount of segments that a player gets when they eat food'
    )
    initial_segments = models.PositiveIntegerField(
        verbose_name='Initial Segments',
        default=4,
        help_text='The amount of segments that a player should start with'
    )
    max_segments = models.PositiveIntegerField(
        verbose_name='Maximum Segments',
        blank=True,
        null=True,
        default=None,
        help_text='The maximum amount of segments that any given player can have'
    )

    class Meta:
        verbose_name = "Snake Game Server"
        verbose_name_plural = "Snake Game Servers"

    def __str__(self):
        return f"SnakeGameServer{{max_players={self.max_players}}}"
