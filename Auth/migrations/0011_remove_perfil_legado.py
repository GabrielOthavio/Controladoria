from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Auth', '0010_rbac_perfil'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='perfil_legado',
        ),
    ]
