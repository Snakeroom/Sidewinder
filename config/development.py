# Django development configuration

from .base import *

DEBUG = True

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Channels

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}

# CORS, CSRF & Security
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8000",
]

CSRF_TRUSTED_ORIGINS = [
    "localhost:8000",
]

ALLOWED_HOSTS = []
SECRET_KEY = 'e(vd8&i11%s2=yxhd-1jm=4lb@vq+!569e1n^1yxh%9&s%a+ot'
