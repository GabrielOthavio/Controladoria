# /Auth/urls/tipo_acao_urls.py
from django.urls import path
from .. import views

urlpatterns = [
    path('tipos-acao/', views.lista_tipos_acao, name='lista_tipos_acao'),
    path('tipos-acao/adicionar/', views.adicionar_tipo_acao, name='adicionar_tipo_acao'),
    path('tipos-acao/<uuid:id_unico>/editar/', views.editar_tipo_acao, name='editar_tipo_acao'),
    path('tipos-acao/<uuid:id_unico>/excluir/', views.excluir_tipo_acao, name='excluir_tipo_acao'),
]