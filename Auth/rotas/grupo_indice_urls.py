# /Auth/urls/tipo_acao_urls.py
from django.urls import path
from .. import views

urlpatterns = [
    # --- Gerenciamento de Grupos de Índice (CRUD - APENAS CHEFE) ---
    path('grupos-indice/', views.lista_grupos_indice, name='lista_grupos_indice'),
    path('grupos-indice/adicionar/', views.adicionar_grupo_indice, name='adicionar_grupo_indice'),
    path('grupos-indice/<uuid:id_unico>/editar/', views.editar_grupo_indice, name='editar_grupo_indice'),
    path('grupos-indice/<uuid:id_unico>/excluir/', views.excluir_grupo_indice, name='excluir_grupo_indice'),
]