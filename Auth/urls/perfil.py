from django.urls import path
from .. import views

urlpatterns = [
    path('perfis/', views.lista_perfis, name='lista_perfis'),
    path('perfis/adicionar/', views.adicionar_perfil, name='adicionar_perfil'),
    path('perfis/<uuid:id_unico>/editar/', views.editar_perfil, name='editar_perfil'),
    path('perfis/<uuid:id_unico>/excluir/', views.excluir_perfil, name='excluir_perfil'),
]
