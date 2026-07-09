import uuid

import encrypted_model_fields.fields
from django.db import migrations, models


def recriptografar_achados_existentes(apps, schema_editor):
    """
    A AlterField sozinha só muda o tipo da coluna — não recriptografa linhas
    já existentes. Re-salva cada Achado para que o EncryptedTextField cifre
    o conteúdo que hoje está em texto plano.
    """
    Achado = apps.get_model('Auth', 'Achado')
    for achado in Achado.objects.all().iterator():
        achado.save(update_fields=['descricao'])


def reverter_recriptografia(apps, schema_editor):
    # Irreversível de forma automática (não há como saber o texto plano
    # original sem decifrar) — a reversão da AlterField já basta para poder
    # rodar `migrate Auth 0015` sem quebrar o schema.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0015_usuario_unidade_escopo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achado',
            name='descricao',
            field=encrypted_model_fields.fields.EncryptedTextField(verbose_name='Descrição do Achado'),
        ),
        migrations.AddField(
            model_name='achado',
            name='origem_mobile_uuid',
            field=models.UUIDField(blank=True, null=True, unique=True, verbose_name='UUID de Origem (Mobile)'),
        ),
        migrations.RunPython(recriptografar_achados_existentes, reverter_recriptografia),
    ]
