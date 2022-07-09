from datetime import timezone
from django.forms import ValidationError
from rest_framework import serializers
from api.models import Game, HighScore, Move, User, UserProfile

from django.contrib.sessions.models import Session
from django.utils import timezone


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

    class Meta:
        model = Game
        fields = "__all__"

    def validate_players(self, players):
        login_users = self._get_all_logged_in_users()
        login_players = list()
        for user in login_users:
            login_players.append(user.profile)
        if len(players) > self.initial_data["max_players_number"]:
            raise ValidationError("Maximum count of players reached.")
        for player in players:
            if player not in login_players:
                raise ValidationError("Player must be login.")
        return players

    def create(self, validated_data):
        Move.objects.all().delete()
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
        fields = "__all__"


class GamePlayPartialUpdateSerializer(serializers.ModelSerializer):
    current_moves = MoveSerializer(read_only=True)

    class Meta:
        model = Game
        fields = (
            "current_player",
            "current_moves",
        )

    def validate_current_player(self, current_player):
        if current_player.id in self.players:
            return current_player
        else:
            raise serializers.ValidationError(
                "This player isn't one of the current players of this game."
            )

    def update(self, instance, validated_data):
        if self._is_move_valid(validated_data["move"]):
            self.process_move(validated_data["move"])
            if self.is_tied() or self.has_winner:
                self.is_done = True
            elif self.has_winner == True:
                time_stop = timezone.now()
                duration = time_stop - self.created_date
                moves = self.current_moves.objects.filter(
                    player=self.current_player
                ).count()
                HighScore.objects.create(
                    player=self.current_player,
                    duration_time=duration,
                    moves_count=moves,
                )
                self.is_done = True
            else:
                # -- switch player --
                pass

    def _is_move_valid(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col
        move_was_not_played = (
            Move.objects.filter(row=row, col=col, player=move.player) == None
        )
        no_winner = not self.has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        """Process the current move and check if it's a win."""
        row, col = move.row, move.col
        self.current_moves.add(move)
        self.current_moves.save()
        for combo in self.winning_combinations:
            results = list(
                Move.objects.filter(row=n, col=m, plyer=move.player) for n, m in combo
            )
            is_win = len(results) == self.board_size
            if is_win:
                self.has_winner = True
                self.winner_combination = combo
                self.is_done = True
                break

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self.has_winner
        played_moves = (move.player for row in self.current_moves for move in row)
        return no_winner and all(played_moves)
