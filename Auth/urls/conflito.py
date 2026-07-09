from django.urls import path
from ..views import conflitos_views

urlpatterns = [
    path('conflitos/', conflitos_views.listar_conflitos, name='listar_conflitos'),
    path('conflitos/<uuid:id_unico>/resolver/', conflitos_views.resolver_conflito, name='resolver_conflito'),
]
