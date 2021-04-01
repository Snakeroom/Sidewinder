from django.urls import path

from . import views

urlpatterns = [
    path('tokens', views.get_owned_tokens),
    path('scripts', views.get_user_scripts),
]
