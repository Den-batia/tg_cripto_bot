# Generated by Django 3.0.8 on 2020-10-18 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0026_auto_20200926_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbol',
            name='info',
            field=models.TextField(default=''),
        ),
    ]
