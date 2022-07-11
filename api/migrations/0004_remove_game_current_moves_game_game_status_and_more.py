# Generated by Django 4.0.5 on 2022-07-11 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_highscore_player_move_game'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='current_moves',
        ),
        migrations.AddField(
            model_name='game',
            name='game_status',
            field=models.JSONField(null=True, blank=True, default=dict)
        ),
        migrations.DeleteModel(
            name='Move',
        ),
    ]
