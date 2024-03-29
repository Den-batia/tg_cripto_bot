# Generated by Django 3.0.8 on 2020-09-03 20:22

from django.db import migrations, models


def add_symbols(apps, schema_editor):
    Symbol = apps.get_model("api", "Symbol")
    db_alias = schema_editor.connection.alias
    Symbol.objects.using(db_alias).create(name='usdt', min_withdraw=10, commission=5)
    Symbol.objects.using(db_alias).create(name='prizm', min_withdraw=10, commission=1)


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0013_dispute_initiator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symbol',
            name='name',
            field=models.CharField(max_length=5, unique=True),
        ),
        migrations.RunPython(add_symbols)
    ]
