# /Auth/rotas/usuario_urls.py
from django.urls import path
from ..views.crud_Usuario_views import (
    lista_usuarios,
    adicionar_usuario,
    editar_usuario,
    excluir_usuario,
)

urlpatterns = [
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/adicionar/', adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/editar/<uuid:id_unico>/', editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<uuid:id_unico>/', excluir_usuario, name='excluir_usuario'),
]