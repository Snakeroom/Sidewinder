from django.urls import path

from . import views

urlpatterns = [
    path('@me', views.get_current_user),
    path('@me/profile/', views.edit_profile),
    path('reddit/login/', views.reddit_login),
    path('reddit/authorize/', views.authorize_callback),
]
