from django.urls import path

from . import views

urlpatterns = [
    path('tokens', views.get_owned_tokens)
]
