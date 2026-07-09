from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class Command(BaseCommand):
    """
    Provisionamento manual do vínculo entre um Usuario do Django e o Usuario
    correspondente no Prisma do sync-backend (mobile/sync-backend). Não faz
    a escrita no Prisma diretamente (o Django não tem acesso a esse banco) —
    apenas resolve o id_unico do Django e imprime o comando pronto para
    colar, reduzindo o provisionamento manual a um copiar-e-colar em vez de
    procurar/transcrever o UUID à mão em dois sistemas.

    Uso: python manage.py vincular_usuario_mobile <username>
    """

    help = 'Gera o comando de vínculo do Usuario do Django com o Usuario do sync-backend mobile.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)

    def handle(self, *args, **options):
        username = options['username']
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            raise CommandError(f'Usuário "{username}" não encontrado.')

        self.stdout.write(self.style.SUCCESS(
            f'Usuário "{username}" — id_unico = {usuario.id_unico}'
        ))
        self.stdout.write('')
        self.stdout.write('Cole no psql do banco do sync-backend (mobile/sync-backend), '
                           'substituindo <username_mobile> pelo username já cadastrado lá:')
        self.stdout.write(self.style.WARNING(
            f'UPDATE usuarios SET django_usuario_uuid = \'{usuario.id_unico}\' '
            f'WHERE username = \'<username_mobile>\';'
        ))
