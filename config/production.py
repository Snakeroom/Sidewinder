# Django production config file

from .base import *
import environ

env = environ.Env()

# CORS, CSRF & Security

CORS_ORIGIN_WHITELIST = [
    "https://snakeroom.org",
    "https://api.snakeroom.org",
]

CSRF_TRUSTED_ORIGINS = [
    "snakeroom.org",
    "api.snakeroom.org",
]

# SECRET_KEY = TODO

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': env.db(default='postgresql:///sidewinder')
}
