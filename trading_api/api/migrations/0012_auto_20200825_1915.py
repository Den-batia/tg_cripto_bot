# Generated by Django 3.0.8 on 2020-08-25 19:15

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_user_last_nickname_change'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_system_active',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Dispute',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deal', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dispute', to='api.Deal')),
            ],
        ),
    ]