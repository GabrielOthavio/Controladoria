from django import template

register = template.Library()


@register.simple_tag
def pode(usuario, tela, acao='ver'):
    """
    Uso: {% pode request.user 'acoes' 'criar' as can_create %}
         {% if can_create %}...{% endif %}
    """
    if not usuario or not usuario.is_authenticated:
        return False
    return usuario.tem_permissao(tela, acao)


@register.filter
def get_item(dicionario, chave):
    """Acessa dict por chave variável no template: dict|get_item:chave"""
    if dicionario is None:
        return None
    return dicionario.get(chave)
