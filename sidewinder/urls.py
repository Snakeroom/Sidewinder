"""sidewinder URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from channels.routing import URLRouter
from django.contrib import admin
from django.urls import path, include

from sidewinder.sneknet.channel_master import SneknetConsumer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('identity/', include('sidewinder.identity.urls')),
]

socket_routes = URLRouter([
    path('', SneknetConsumer)
])
