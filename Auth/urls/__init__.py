from django.urls import path, include

app_name = 'Auth'

urlpatterns = [
    path('', include('Auth.urls.auth')),
    path('', include('Auth.urls.usuario')),
    path('', include('Auth.urls.acao')),
    path('', include('Auth.urls.auditoria')),
    path('', include('Auth.urls.matriz_auditoria')),
    path('', include('Auth.urls.entidade_auditoria')),
    path('', include('Auth.urls.indice')),
    path('', include('Auth.urls.tipo_acao')),
    path('', include('Auth.urls.tipo_indice')),
    path('', include('Auth.urls.grupo_indice')),
    path('', include('Auth.urls.api')),
    path('', include('Auth.urls.perfil')),
]
