# /Auth/urls/auth_urls.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .. import views
from ..forms import CustomAuthenticationForm

urlpatterns = [
    # --- Autenticação ---
    path('login/', auth_views.LoginView.as_view(template_name='login.html',authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('Auth:login')), name='logout'),
    # --- Páginas Principais e Registro ---
    path('register/', views.register, name='register'),
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('', views.dashboard, name='dashboard'),
]