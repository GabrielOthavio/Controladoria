from django.urls import path
from ..views import api_mobile_views

urlpatterns = [
    path('api/mobile/auditorias/', api_mobile_views.api_mobile_auditorias, name='api_mobile_auditorias'),
    path('api/mobile/auditorias/<uuid:id_unico>/etapas/', api_mobile_views.api_mobile_etapas, name='api_mobile_etapas'),
    path('api/mobile/achados/', api_mobile_views.api_mobile_criar_achado, name='api_mobile_criar_achado'),
    path('api/mobile/etapas/', api_mobile_views.api_mobile_criar_etapa, name='api_mobile_criar_etapa'),
    path('api/mobile/etapas/<uuid:id_unico>/editar/', api_mobile_views.api_mobile_editar_etapa, name='api_mobile_editar_etapa'),
    path('api/mobile/etapas/<uuid:id_unico>/excluir/', api_mobile_views.api_mobile_excluir_etapa, name='api_mobile_excluir_etapa'),
]
