# Generated by Django 2.1.7 on 2019-12-12 01:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0005_game_winner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='move',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
    ]
