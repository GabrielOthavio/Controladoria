from django.urls import path
from .. import views

urlpatterns = [
    path('matrizes/', views.lista_matrizes, name='lista_matrizes'),
    path('matrizes/adicionar/', views.adicionar_matriz, name='adicionar_matriz'),
    path('matrizes/<uuid:id_unico>/editar/', views.editar_matriz, name='editar_matriz'),
    path('matrizes/<uuid:id_unico>/excluir/', views.excluir_matriz, name='excluir_matriz'),
]
