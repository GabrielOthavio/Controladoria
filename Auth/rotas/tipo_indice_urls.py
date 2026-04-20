# /Auth/urls/tipo_indice_urls.py
from django.urls import path
from .. import views

urlpatterns = [
    path('tipos-indice/', views.lista_tipos_indice, name='lista_tipos_indice'),
    path('tipos-indice/adicionar/', views.adicionar_tipo_indice, name='adicionar_tipo_indice'),
    path('tipos-indice/editar/<uuid:id_unico>/', views.editar_tipo_indice, name='editar_tipo_indice'),
    path('tipos-indice/excluir/<uuid:id_unico>/', views.excluir_tipo_indice, name='excluir_tipo_indice'),
]