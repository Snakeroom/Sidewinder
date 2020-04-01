from django.apps import apps

import importlib
import logging

from . import channel_master

log = logging.getLogger(__name__)

def find_channel_handlers():
    handler_map = {}

    for app in apps.get_app_configs():
        try:
            channel_mod = importlib.import_module('.channels', app.name)
        except ModuleNotFoundError:
            continue

        if not hasattr(channel_mod, 'handlers'):
            continue

        try:
            for msg_type, handler in getattr(channel_mod, 'handlers'):
                if msg_type in handler_map:
                    log.warning(f"A handler already exists for message type {msg_type}, {app.name} is overriding!")

                handler_map[msg_type] = handler
        except TypeError:
            raise LookupError("handlers key found in channels module, but it is not iterable or badly formatted."
                              "correct style is [\n\t('typename', callable),\n]")

    channel_master.all_socket_handlers = handler_map
