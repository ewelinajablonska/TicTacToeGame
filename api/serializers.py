from datetime import datetime, timezone
from django.forms import ValidationError
from rest_framework import serializers
from api.models import Game, HighScore, Move, User, UserProfile

from django.contrib.sessions.models import Session
from django.utils import timezone
from gettext import gettext as _

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("title", "address", "country", "city")


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer(required=True)

    class Meta:
        model = User
        fields = ("url", "email", "first_name", "last_name", "password", "profile")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        profile = instance.profile

        instance.email = validated_data.get("email", instance.email)
        instance.save()
        # assign nested fields
        profile.title = profile_data.get("title", profile.title)
        profile.address = profile_data.get("address", profile.address)
        profile.country = profile_data.get("country", profile.country)
        profile.city = profile_data.get("city", profile.city)
        profile.save()

        return instance


class DashboardSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(read_only=True)
    date = serializers.ReadOnlyField()
    duration_time = serializers.ReadOnlyField()
    moves_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = HighScore
        fields = "__all__"


class GamePlaySerializer(serializers.ModelSerializer):
    winning_combinations = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(default=None, allow_null=True)
        )
    )
    winner_combination = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(default=None, allow_null=True)
        )
    )
    # status = serializers.ListField(
    #     child=serializers.IntegerField(default=None, allow_null=True)
    # )

    class Meta:
        model = Game
        fields = "__all__"

    def validate_players(self, players):
        login_users = self._get_all_logged_in_users()
        login_players = list()
        for user in login_users:
            login_players.append(user.profile)
        if len(players) > self.initial_data["max_players_number"]:
            raise ValidationError(_("Maximum count of players reached."))
        for player in players:
            if player not in login_players:
                raise ValidationError(_("Player must be login."))
        return players

    def create(self, validated_data):
        self._setup(validated_data)
        game = super().create(validated_data)
        all_possible_moves = Move.objects.all()
        game.winning_combinations = self._get_winning_combinations(all_possible_moves)
        game.save()
        return game

    def _setup(self, validated_data):
        # set players
        validated_data["current_player"] = validated_data["players"][0]
        # set created_date
        validated_data["created_date"] = timezone.now()
        # define how to store moves
        all_possible_moves = [
            Move.objects.create(row=row, col=col)
            for col in range(validated_data["board_size"])
            for row in range(validated_data["board_size"])
        ]

    def _get_all_logged_in_users(self):
        # Query all non-expired sessions
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get("_auth_user_id", None))

        # Query all logged in users based on id list
        return User.objects.filter(id__in=uid_list)

    def _get_winning_combinations(self, all_possible_moves):
        rows = [
            list(Move.objects.filter(row=move.row).values_list("id", flat=True))
            for move in all_possible_moves[: self.data["board_size"]]
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        winning_combinations = rows + columns + [first_diagonal, second_diagonal]
        return winning_combinations


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = (
            "row",
            "col",
            "player",
        )


class GamePlayPartialUpdateSerializer(serializers.ModelSerializer):
    current_moves = MoveSerializer()

    class Meta:
        model = Game
        fields = (
            "current_moves",
        )

    def validate_current_moves(self, current_moves):
        if current_moves['player'] == self.instance.current_player:
            return current_moves
        else:
            raise serializers.ValidationError(
                _("This player isn't the current player.")
            )

    def update(self, instance, validated_data):
        if self._is_move_valid(validated_data["current_moves"]):
            self.process_move(validated_data["current_moves"])
            if self.is_tied():
                instance.is_done = True
                # instance.status = Move.objects.values_list('id','player')
                instance.save()
                return instance
            elif instance.has_winner == True:
                time_stop = datetime.now()
                duration = time_stop - instance.created_date
                moves = self.current_moves.objects.filter(
                    player=self.current_player
                ).count()
                import pdb;pdb.set_trace()
                HighScore.objects.create(
                    player=self.current_player,
                    duration_time=duration,
                    moves_count=moves,
                )
                # instance.status = Move.objects.values_list('id','player')
                instance.save()
                Move.objects.all().delete()
                return instance
            else:
                import pdb;pdb.set_trace()
                instance.current_player = instance.players.exclude(id=instance.current_player.id)[0]
                instance.save()
                return instance
        else:
            raise serializers.ValidationError(
                _("This move is invalid - check if it has been made or if the game has ended.")
            )

    def _is_move_valid(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col, player = move['row'], move['col'], move['player']
        move_was_not_played = (
            len(Move.objects.filter(row=row, col=col, player=player)) == 0
        )
        no_winner = not self.instance.has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        """Process the current move and check if it's a win."""
        row, col = move['row'], move['col']
        updated_move = Move.objects.get(row=row, col=col)
        updated_move.player = self.instance.current_player
        updated_move.save()
        for combo in self.instance.winning_combinations:
            results = list(
                Move.objects.filter(id=obj, player=updated_move.player) for obj in combo
            )
            for result in results:
                if len(result) == 0: 
                    results.remove(result)
            is_win = len(results) == self.instance.board_size
            if is_win:
                self.instance.has_winner = True
                self.instance.winner_combination = combo
                self.instance.is_done = True
                self.instance.save()
                break
            continue

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self.instance.has_winner
        no_played_moves = (Move.objects.filter(player=None))
        return no_winner and len(no_played_moves) == 0
