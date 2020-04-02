# Django production config file

from .base import *
import environ

env = environ.Env()

STATIC_ROOT = env('STATIC_ROOT', default="static/")

# CORS, CSRF & Security

CORS_ORIGIN_WHITELIST = [
    "https://snakeroom.org",
    "https://api.snakeroom.org",
    "https://gremlins-api.reddit.com",
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
