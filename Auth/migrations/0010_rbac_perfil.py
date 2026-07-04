from django.db import migrations, models
import django.db.models.deletion
import uuid


TELAS = [
    'dashboard', 'acoes', 'indices', 'tipos_acao', 'tipos_indice',
    'grupos_indice', 'auditorias', 'matrizes', 'entidades', 'usuarios', 'perfis',
]

FUNC_PERMS = {
    'dashboard':     (True,  False, False, False),
    'acoes':         (True,  True,  True,  True),
    'indices':       (True,  True,  True,  True),
    'tipos_acao':    (True,  False, False, False),
    'tipos_indice':  (True,  False, False, False),
    'grupos_indice': (False, False, False, False),
    'auditorias':    (True,  False, False, False),
    'matrizes':      (True,  False, False, False),
    'entidades':     (True,  False, False, False),
    'usuarios':      (False, False, False, False),
    'perfis':        (False, False, False, False),
}


def criar_perfis_padrao(apps, schema_editor):
    Perfil = apps.get_model('Auth', 'Perfil')
    PerfilPermissao = apps.get_model('Auth', 'PerfilPermissao')
    Usuario = apps.get_model('Auth', 'Usuario')

    chefe, _ = Perfil.objects.get_or_create(
        nome='Chefe',
        defaults={'descricao': 'Acesso total ao sistema.'},
    )
    for tela in TELAS:
        PerfilPermissao.objects.get_or_create(
            perfil=chefe, tela=tela,
            defaults={'pode_ver': True, 'pode_criar': True, 'pode_editar': True, 'pode_excluir': True},
        )

    funcionario, _ = Perfil.objects.get_or_create(
        nome='Funcionário',
        defaults={'descricao': 'Acesso básico — gerencia apenas as próprias ações e visualiza os demais módulos.'},
    )
    for tela, (v, c, e, d) in FUNC_PERMS.items():
        PerfilPermissao.objects.get_or_create(
            perfil=funcionario, tela=tela,
            defaults={'pode_ver': v, 'pode_criar': c, 'pode_editar': e, 'pode_excluir': d},
        )

    for usuario in Usuario.objects.all():
        legado = usuario.perfil_legado or 'FUNCIONARIO'
        usuario.perfil = chefe if legado == 'CHEFE' else funcionario
        usuario.save(update_fields=['perfil'])


def restaurar_perfil_legado(apps, schema_editor):
    Usuario = apps.get_model('Auth', 'Usuario')
    for usuario in Usuario.objects.all():
        if usuario.perfil_id:
            usuario.perfil_legado = 'CHEFE' if usuario.perfil.nome == 'Chefe' else 'FUNCIONARIO'
            usuario.save(update_fields=['perfil_legado'])


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0009_acao_status_unidade_paint'),
    ]

    operations = [
        # 1. Criar tabela Perfil
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_unico', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('nome', models.CharField(max_length=100, unique=True, verbose_name='Nome')),
                ('descricao', models.TextField(blank=True, default='', verbose_name='Descrição')),
            ],
            options={'verbose_name': 'Perfil', 'verbose_name_plural': 'Perfis', 'ordering': ['nome']},
        ),

        # 2. Criar tabela PerfilPermissao
        migrations.CreateModel(
            name='PerfilPermissao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tela', models.CharField(
                    max_length=30, verbose_name='Tela',
                    choices=[
                        ('dashboard', 'Dashboard'), ('acoes', 'Ações'), ('indices', 'Índices'),
                        ('tipos_acao', 'Tipos de Ação'), ('tipos_indice', 'Tipos de Índice'),
                        ('grupos_indice', 'Grupos de Índice'), ('auditorias', 'Auditorias'),
                        ('matrizes', 'Matrizes de Auditoria'), ('entidades', 'Entidades de Auditoria'),
                        ('usuarios', 'Usuários'), ('perfis', 'Perfis'),
                    ],
                )),
                ('pode_ver',     models.BooleanField(default=False, verbose_name='Ver')),
                ('pode_criar',   models.BooleanField(default=False, verbose_name='Criar')),
                ('pode_editar',  models.BooleanField(default=False, verbose_name='Editar')),
                ('pode_excluir', models.BooleanField(default=False, verbose_name='Excluir')),
                ('perfil', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='permissoes',
                    to='Auth.perfil',
                )),
            ],
            options={
                'verbose_name': 'Permissão',
                'verbose_name_plural': 'Permissões',
                'unique_together': {('perfil', 'tela')},
            },
        ),

        # 3. Renomear campo antigo para preservar dados durante migração
        migrations.RenameField(
            model_name='usuario',
            old_name='perfil',
            new_name='perfil_legado',
        ),

        # 4. Adicionar novo campo FK (null temporariamente)
        migrations.AddField(
            model_name='usuario',
            name='perfil',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='usuarios',
                to='Auth.perfil',
                verbose_name='Perfil',
            ),
        ),

        # 5. Migrar dados: criar perfis padrão e atribuir aos usuários
        migrations.RunPython(criar_perfis_padrao, restaurar_perfil_legado),

        # 6. Tornar FK obrigatória
        migrations.AlterField(
            model_name='usuario',
            name='perfil',
            field=models.ForeignKey(
                null=False, blank=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='usuarios',
                to='Auth.perfil',
                verbose_name='Perfil',
            ),
        ),
    ]
