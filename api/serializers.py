from typing import List
from django.forms import ValidationError
from rest_framework import serializers
from api.models import Game, HighScore, UserProfile

from django.utils import timezone
from gettext import gettext as _
import logging

log = logging.getLogger("orders")


class DashboardSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.ReadOnlyField()
    duration_time = serializers.ReadOnlyField()
    moves_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = HighScore
        fields = "__all__"


class GamePlaySerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(
        many=True, queryset=UserProfile.objects.all()
    )
    winning_combinations = serializers.ListField(
        child=serializers.ListField(child=serializers.IntegerField(required=False)),
        required=False,
    )
    winner_combination = serializers.ListField(
        child=serializers.IntegerField(required=False), required=False
    )

    class Meta:
        model = Game
        fields = "__all__"

    def validate_players(self, players):
        all_players = UserProfile.objects.all()
        if len(players) > int(self.initial_data["max_players_number"]):
            raise ValidationError(_("Maximum count of players reached."))
        elif len(players) < 2:
            raise ValidationError(_("Minimum count of players reached."))
        for player in players:
            if player not in all_players:
                raise ValidationError(
                    _("Player (id: {}) must be registered.").format(player.id)
                )
        return players

    def create(self, validated_data):
        all_possible_moves, validated_data = self._setup(validated_data)
        players = validated_data.pop("players")
        game = super().create(validated_data)
        game.players.set(players)
        game.current_player = players[0]
        game.created_date = timezone.now()
        players_id = [player.id for player in players]
        game.game_status = {value: [] for value in players_id}
        game.winning_combinations = self._get_winning_combinations(all_possible_moves)
        game.save()
        log.info(_("Good luck to both of you. Let's the game begin!"))
        return game

    def _setup(self, validated_data: dict):
        # set players
        validated_data["current_player"] = validated_data["players"][0]
        # set created_date
        validated_data["created_date"] = timezone.now()
        # define how to store moves
        all_possible_moves = [k for k in range(validated_data["board_size"] ** 2)]
        # setup players status
        players_id = [player.id for player in validated_data["players"]]
        validated_data["game_status"] = {value: [] for value in players_id}
        return all_possible_moves, validated_data

    def _get_winning_combinations(self, all_possible_moves: List[int]) -> List[List[int]]:
        length = len(all_possible_moves)
        col_number = int(self.initial_data["board_size"])
        columns = [
            all_possible_moves[
                i * length // col_number : (i + 1) * length // col_number
            ]
            for i in range(col_number)
        ]
        rows = [list(col) for col in zip(*columns)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        winning_combinations = rows + columns + [first_diagonal, second_diagonal]
        return winning_combinations


class GamePlayPartialUpdateSerializer(serializers.ModelSerializer):
    move = serializers.IntegerField(allow_null=True)

    class Meta:
        model = Game
        fields = ("move",)

    def validate_move(self, move: int) -> int:
        moves_list = list(self.instance.game_status.values())
        move_was_not_played = move not in [obj for list in moves_list for obj in list]
        move_is_in_current = move in [k for k in range(self.instance.board_size**2)]
        no_winner = not self.instance.has_winner

        if no_winner and move_was_not_played and move_is_in_current:
            return move
        elif not no_winner:
            raise serializers.ValidationError(_("This game is over."))
        else:
            raise serializers.ValidationError(_("Move is not valid."))

    def to_representation(self, value):
        return value.game_status

    def update(self, instance, validated_data):
        self.process_move(validated_data["move"])
        if self.is_tied():
            instance.is_done = True
            instance.save()
            log.info(_("Game draw! Feel free to try again. Good luck!"))
            return instance
        elif instance.has_winner == True:
            time_stop = timezone.now()
            duration = time_stop - instance.created_date
            moves = len(instance.game_status[str(instance.current_player.id)])
            HighScore.objects.create(
                player=instance.current_player,
                duration_time=duration,
                moves_count=moves,
            )
            log.info(
                _("Congrats for player {}! Good game! Feel free to try again.").format(
                    instance.current_player
                )
            )
            return instance
        else:
            instance.current_player = instance.players.exclude(
                id=instance.current_player.id
            )[0]
            instance.save()
            log.info(_("Player's {} turn.").format(instance.current_player))
            return instance

    def process_move(self, move: int) -> None:
        """Process the current move and check if it's a win."""
        player_id = self.instance.current_player.id
        self.instance.game_status[str(player_id)].append(move)
        self.instance.save()
        for combo in self.instance.winning_combinations:
            played_moves = self.instance.game_status[str(player_id)]
            is_win = all(item in played_moves for item in combo)
            if is_win:
                self.instance.has_winner = True
                self.instance.winner_combination = combo
                self.instance.is_done = True
                self.instance.save()
                break
            continue

    def is_tied(self) -> bool:
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self.instance.has_winner

        moves_list = list(self.instance.game_status.values())
        played_moves = [obj for list in moves_list for obj in list]
        all_moves = [k for k in range(self.instance.board_size**2)]
        no_played_moves = all(item in played_moves for item in all_moves)

        return no_winner and no_played_moves
