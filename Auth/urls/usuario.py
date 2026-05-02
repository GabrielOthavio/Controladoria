from django.urls import path
from .. import views

urlpatterns = [
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/adicionar/', views.adicionar_usuario, name='adicionar_usuario'),
    path('usuarios/<uuid:id_unico>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<uuid:id_unico>/excluir/', views.excluir_usuario, name='excluir_usuario'),
]
