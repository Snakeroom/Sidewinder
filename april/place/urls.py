from django.urls import path

from . import views

urlpatterns = [
    path('projects', views.get_projects),
    path('projects/<uuid:uuid>/membership', views.join_project),
    path('projects/<uuid:uuid>/create_division', views.create_division),
    path('projects/<uuid:uuid>/bitmap', views.get_bitmap_for_project),
    path('projects/<uuid:uuid>', views.manage_project),
    path('projects/<uuid:uuid>/divisions', views.get_divisions),
    path('projects/<uuid:project_uuid>/divisions/<uuid:division_uuid>', views.manage_division),
    path('bitmap', views.get_bitmap),
]
