from . import views

handlers = [
    ('second:heartbeat', views.keepalive),
    ('second:report', views.report),
]
