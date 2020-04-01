from django.urls import path

from . import views

urlpatterns = [
    path('submit', views.submit_known_answers),
    path('query', views.query_answers),
    path('recent', views.fetch_recent),
    path('check', views.check_answer),
]
