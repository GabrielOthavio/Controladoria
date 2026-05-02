# Arquivo: config/urls.py (na pasta principal do seu projeto)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apenas uma linha para conectar todas as URLs do seu aplicativo 'Auth'
    path('', include('Auth.urls')),
]