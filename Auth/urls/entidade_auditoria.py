from django.urls import path
from .. import views

urlpatterns = [
    path('entidades/', views.lista_entidades, name='lista_entidades'),
    path('entidades/adicionar/', views.adicionar_entidade, name='adicionar_entidade'),
    path('entidades/<uuid:id_unico>/editar/', views.editar_entidade, name='editar_entidade'),
    path('entidades/<uuid:id_unico>/excluir/', views.excluir_entidade, name='excluir_entidade'),
]
