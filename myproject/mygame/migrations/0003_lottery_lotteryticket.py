# Generated by Django 5.0.6 on 2024-05-26 14:08

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mygame', '0002_emailotp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lottery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lottery_code', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('tickets_remaining', models.IntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='LotteryTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('lottery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='mygame.lottery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lottery_tickets', to='mygame.userprofile')),
            ],
        ),
    ]
