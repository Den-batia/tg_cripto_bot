# Generated by Django 3.0.8 on 2020-07-23 15:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200722_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='api.User'),
        ),
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(max_length=4),
        ),
    ]
