# Arquivo: Auth/urls.py

from django.urls import path, include

app_name = 'Auth'

urlpatterns = [
    # Delega as rotas para cada arquivo correspondente
    path('', include('Auth.rotas.auth_urls')),
    path('', include('Auth.rotas.acao_urls')),
    path('', include('Auth.rotas.indice_urls')),
    path('', include('Auth.rotas.tipo_acao_urls')),
    path('', include('Auth.rotas.tipo_indice_urls')),
    path('', include('Auth.rotas.grupo_indice_urls')),
    path('', include('Auth.rotas.usuario_urls')),
]