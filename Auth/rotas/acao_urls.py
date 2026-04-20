# /Auth/urls/tipo_acao_urls.py
from django.urls import path
from .. import views

urlpatterns = [
    path('acoes/', views.lista_acoes, name='lista_acoes'),
    path('acoes/adicionar/', views.adicionar_acao, name='adicionar_acao'),
    path('acoes/<uuid:id_unico>/editar/', views.editar_acao, name='editar_acao'),
    path('acoes/<uuid:id_unico>/excluir/', views.excluir_acao, name='excluir_acao'),
]