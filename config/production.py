# Django production config file

# noinspection PyUnresolvedReferences
from .base import *

import environ
import sentry_sdk

from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env()

if "SENTRY_DSN" in env:
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[DjangoIntegration()],

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True
    )

STATIC_ROOT = env('STATIC_ROOT', default="static/")

# CORS, CSRF & Security

CORS_ORIGIN_WHITELIST = [
    "https://snakeroom.org",
    "https://api.snakeroom.org",
    "https://second-api.reddit.com",
]

ALLOWED_HOSTS = CSRF_TRUSTED_ORIGINS = [
    "snakeroom.org",
    "api.snakeroom.org",
]

SECRET_KEY = env('SECRET_KEY')

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db(default='postgresql:///sidewinder')
}

# Cache

CACHES = {
    'default': env.cache(default='rediscache://localhost:6379/1')
}

SOLO_CACHE = 'default'
SOLO_CACHE_TIMEOUT = 1200

# Channels

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6397)]
        }
    }
}
