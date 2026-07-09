import threading
from contextlib import contextmanager

_thread_local = threading.local()


def get_current_user():
    return getattr(_thread_local, 'user', None)


@contextmanager
def set_current_user(usuario):
    """
    Usado pelas views internas chamadas pelo sync-backend (NestJS), fora do
    ciclo normal de request/CurrentUserMiddleware: impersona o auditor real
    durante a criação de um Achado via API interna, para que os signals de
    Audit by Design (HistoricoAlteracoes) atribuam a alteração a ele — e não
    a None/"Sistema".
    """
    anterior = getattr(_thread_local, 'user', None)
    _thread_local.user = usuario
    try:
        yield
    finally:
        _thread_local.user = anterior


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_local.user = getattr(request, 'user', None)
        try:
            response = self.get_response(request)
        finally:
            _thread_local.user = None
        return response
