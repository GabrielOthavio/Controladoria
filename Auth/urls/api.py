from django.urls import path
from ..views import api_views

urlpatterns = [
    path('api/dashboard/',  api_views.api_dashboard,  name='api_dashboard'),
    path('api/historico/',  api_views.api_historico,  name='api_historico'),
    path('api/auditorias/', api_views.api_auditorias, name='api_auditorias'),
    path('api/acoes/',      api_views.api_acoes,      name='api_acoes'),
]
