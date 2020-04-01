# Django production config file

from .base import *
import environ

env = environ.Env()

# CORS, CSRF & Security

CORS_ORIGIN_WHITELIST = [
    "https://snakeroom.org",
    "https://api.snakeroom.org",
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

# Channels

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6397)]
        }
    }
}
