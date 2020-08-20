# Generated by Django 3.0.8 on 2020-08-19 18:52

import api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_order_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.CharField(default=api.models.random_deal_id, max_length=15, primary_key=True, serialize=False)),
                ('requisite', models.CharField(blank=True, default='', max_length=128)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('state', models.SmallIntegerField(default=0)),
                ('amount_crypto', models.DecimalField(decimal_places=8, max_digits=15)),
                ('amount_currency', models.DecimalField(decimal_places=2, max_digits=15)),
                ('commission', models.DecimalField(decimal_places=8, default=0, max_digits=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('closed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='buyer_deals', to='api.User')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deals', to='api.Order')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seller_deals', to='api.User')),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='deals', to='api.Symbol')),
            ],
        ),
        migrations.CreateModel(
            name='Requisite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requisite', models.CharField(max_length=128)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requisites', to='api.Broker')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requisites', to='api.User')),
            ],
            options={
                'unique_together': {('user', 'broker')},
            },
        ),
    ]
