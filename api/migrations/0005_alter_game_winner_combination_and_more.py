# Generated by Django 4.0.5 on 2022-07-13 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_alter_game_winner_combination_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="game",
            name="winner_combination",
            field=models.JSONField(default=list, null=True),
        ),
        migrations.AlterField(
            model_name="game",
            name="winning_combinations",
            field=models.JSONField(default=list, null=True),
        ),
    ]
