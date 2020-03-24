from django.urls import path

from . import views

urlpatterns = [
    path(r'reddit/login/', views.reddit_login),
    path(r'reddit/authorize/', views.authorize_callback),
]
