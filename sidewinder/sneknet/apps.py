from django.apps import AppConfig

from sidewinder.sneknet.util import find_channel_handlers


class SneknetConfig(AppConfig):
    name = 'sidewinder.sneknet'

    def ready(self):
        find_channel_handlers()
