from functools import wraps

from django.http import HttpResponseForbidden


def requer_permissao(tela, acao):
    """
    Bloqueia a view se request.user.tem_permissao(tela, acao) for False.
    Deve ser aplicado abaixo de @login_required, para garantir que
    request.user já é um Usuario autenticado.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.tem_permissao(tela, acao):
                return HttpResponseForbidden(f"Sem permissão para {acao} {tela}.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_per_page(request, default=16):
    try:
        per_page = int(request.GET.get('per_page', default))
        if per_page not in (8, 16, 32, 64):
            per_page = default
    except (ValueError, TypeError):
        per_page = default
    return per_page
