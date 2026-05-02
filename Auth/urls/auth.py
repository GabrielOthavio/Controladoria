# /Auth/urls/auth.py
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from .. import views
from ..forms import CustomAuthenticationForm

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('Auth:login')), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', RedirectView.as_view(pattern_name='Auth:dashboard', permanent=False)),
]