# /Auth/urls/tipo_acao_urls.py
from django.urls import path
from .. import views

urlpatterns = [
    # --- Gerenciamento de Índices (CRUD) ---
    path('indices/', views.lista_indices, name='lista_indices'),
    path('indices/adicionar/', views.adicionar_indice, name='adicionar_indice'),
    path('indices/<uuid:id_unico>/editar/', views.editar_indice, name='editar_indice'),
    path('indices/<uuid:id_unico>/excluir/', views.excluir_indice, name='excluir_indice'),
]