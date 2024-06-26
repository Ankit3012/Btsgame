# Generated by Django 5.0.6 on 2024-06-04 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mygame', '0009_lottery_lottery_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('game_name', models.CharField(default='lottery', max_length=200)),
                ('lottery_time', models.CharField(default=3, max_length=200)),
                ('lottery_price', models.CharField(default=10, max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
