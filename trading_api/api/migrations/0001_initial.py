# Generated by Django 3.0.8 on 2020-07-22 20:36
import uuid

import api.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Broker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Symbol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('telegram_id', models.BigIntegerField(blank=True, null=True, unique=True)),
                ('ref_code', models.CharField(default=api.models.random_ref_code, max_length=16, unique=True)),
                ('nickname', models.CharField(default=api.models.random_nickname, max_length=10, unique=True)),
                ('is_admin', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('referred_from', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.User')),
            ],
        ),
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('balance', models.DecimalField(decimal_places=8, default=0, max_digits=15)),
                ('frozen', models.DecimalField(decimal_places=8, default=0, max_digits=15)),
                ('private_key', models.CharField(max_length=128)),
                ('earned_from_ref', models.DecimalField(decimal_places=8, default=0, max_digits=15)),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Symbol')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wallets', to='api.User')),
            ],
        ),
        migrations.CreateModel(
            name='Rates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='rates', to='api.Symbol')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.CharField(default=api.models.random_order_id, max_length=10, primary_key=True, serialize=False)),
                ('limit_from', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('limit_to', models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('rate', models.DecimalField(decimal_places=2, max_digits=10)),
                ('details', models.CharField(default='', max_length=512)),
                ('type', models.CharField(max_length=3)),
                ('broker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='api.Broker')),
                ('symbol', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='api.Symbol')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='api.User')),
            ],
        ),
    ]
