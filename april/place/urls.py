from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.get_projects),
    path('projects/<uuid:uuid>/membership', views.join_project),
]
