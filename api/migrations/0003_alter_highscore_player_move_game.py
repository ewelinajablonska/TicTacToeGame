# Generated by Django 4.0.5 on 2022-07-09 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_highscore'),
    ]

    operations = [
        migrations.AlterField(
            model_name='highscore',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.userprofile'),
        ),
        migrations.CreateModel(
            name='Move',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.IntegerField(blank=True, null=True)),
                ('col', models.IntegerField(blank=True, null=True)),
                ('player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_players_number', models.IntegerField(default=2)),
                ('created_date', models.DateTimeField(blank=True)),
                ('board_size', models.IntegerField(default=3)),
                ('winning_combinations', models.JSONField(blank=True, default=list, null=True)),
                ('is_done', models.BooleanField(default=False)),
                ('has_winner', models.BooleanField(default=False)),
                ('winner_combination', models.JSONField(blank=True, default=list, null=True)),
                ('current_moves', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.move')),
                ('current_player', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_player', to='api.userprofile')),
                ('players', models.ManyToManyField(blank=True, related_name='game_players', to='api.userprofile')),
            ],
        ),
    ]
