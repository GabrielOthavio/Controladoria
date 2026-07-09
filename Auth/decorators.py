from functools import wraps

from django.conf import settings
from django.http import HttpResponseForbidden, JsonResponse


def requer_chave_interna(view_func):
    """
    Protege endpoints chamados servidor-a-servidor pelo sync-backend (NestJS)
    — sem sessão de browser, autenticados por segredo compartilhado
    (X-Internal-Api-Key) e, como defesa em profundidade adicional, por
    allowlist de IP de origem (MOBILE_SYNC_ALLOWED_IPS).
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        chave_recebida = request.headers.get('X-Internal-Api-Key')
        if not chave_recebida or chave_recebida != settings.MOBILE_SYNC_API_KEY:
            return JsonResponse({'detail': 'Chave interna inválida ou ausente.'}, status=403)

        ips_permitidos = settings.MOBILE_SYNC_ALLOWED_IPS
        if ips_permitidos and request.META.get('REMOTE_ADDR') not in ips_permitidos:
            return JsonResponse({'detail': 'Origem não autorizada.'}, status=403)

        return view_func(request, *args, **kwargs)
    return wrapper


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
