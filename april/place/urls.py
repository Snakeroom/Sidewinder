from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.get_projects),
    path('projects/<uuid:uuid>/membership', views.join_project),
    path('projects/<uuid:project_uuid>/create_division', views.create_division),
    path('bitmap', views.get_bitmap),
]

