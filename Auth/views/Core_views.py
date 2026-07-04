from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required(login_url='Auth:login')
def dashboard(request):
    current_user_data = {
        'username': request.user.username,
        'fullName': request.user.get_full_name(),
        'perfil':   request.user.perfil.nome if request.user.perfil_id else '',
        'isChefe':  request.user.tem_permissao('usuarios', 'ver'),
    }
    return render(request, 'spa.html', {'current_user_data': current_user_data})
