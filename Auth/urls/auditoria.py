from django.urls import path
from .. import views

urlpatterns = [
    path('auditorias/',                                                              views.lista_auditorias,    name='lista_auditorias'),
    path('auditorias/adicionar/',                                                    views.adicionar_auditoria, name='adicionar_auditoria'),
    path('auditorias/<uuid:id_unico>/editar/',                                       views.editar_auditoria,    name='editar_auditoria'),
    path('auditorias/<uuid:id_unico>/excluir/',                                      views.excluir_auditoria,   name='excluir_auditoria'),
    path('auditorias/<uuid:id_unico>/gerenciar/',                                    views.gerenciar_auditoria, name='gerenciar_auditoria'),
    # Etapas
    path('auditorias/<uuid:id_unico>/etapas/adicionar/',                             views.adicionar_etapa,     name='adicionar_etapa'),
    path('auditorias/<uuid:id_unico>/etapas/<uuid:etapa_id>/editar/',                views.editar_etapa,        name='editar_etapa'),
    path('auditorias/<uuid:id_unico>/etapas/<uuid:etapa_id>/excluir/',               views.excluir_etapa,       name='excluir_etapa'),
    path('auditorias/<uuid:id_unico>/etapas/<uuid:etapa_id>/reabrir/',               views.reabrir_etapa,       name='reabrir_etapa'),
    # Achados
    path('auditorias/<uuid:id_unico>/etapas/<uuid:etapa_id>/achados/<uuid:achado_id>/excluir/', views.excluir_achado, name='excluir_achado'),
]
