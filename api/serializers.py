from datetime import timezone
from django.forms import ValidationError
from rest_framework import serializers
from api.models import Game, HighScore, Move, User, UserProfile


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
        fields = '__all__'


class GamePlaySerializer(serializers.ModelSerializer):

    class Meta:
        model = Game
        fields = '__all__'

    def create(self, validated_data):
        self._setup()

    def _setup(self):
        # set players
        # TODO--- how to do that, set first player ---
        # set created_date
        self.created_date = timezone.now()
        # get the winnig combinations
        self.winning_combinations = self._get_winning_combinations()
        # define how to store moves
        self.status = [
            Move.objects.create(row=row, col=col) for col in range(self.board_size)
            for row in range(self.board_size)
        ]

    def _get_winning_combinations(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self.current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        winning_combinations = rows + columns + [first_diagonal, second_diagonal]
        return winning_combinations


class MoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Move
        fields = '__all__'


class GamePlayPartialUpdatedSerializer(serializers.ModelSerializer):
    current_moves = MoveSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = (
            'current_player',
            'current_moves',
        )

    def validate_current_player(self, current_player):
        if current_player.id == self.game.player_o or current_player.id == self.game.player_x:
            return current_player
        else: 
            raise serializers.ValidationError(
                "This player isn't one of the current players of this game."
            )

    def update(self, instance, validated_data):
        if self._is_move_valid(validated_data['move']):
            self.process_move(validated_data['move'])
            if self.is_tied() or self.has_winner:
                self.is_done = True
            elif self.has_winner == True:
                self.is_done = True
            else:
                # -- switch player -- 
                pass

    def _is_move_valid(self, move):
        """Return True if move is valid, and False otherwise."""
        row, col = move.row, move.col
        move_was_not_played = Move.objects.filter(
            row=row, col=col, player=move.player
        ) == None
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
            is_win = (len(results) == self.board_size)
            if is_win:
                self.has_winner = True
                self.winner_combination = combo
                self.is_done = True
                break

    def is_tied(self):
        """Return True if the game is tied, and False otherwise."""
        no_winner = not self.has_winner
        played_moves = (
            move.player for row in self.current_moves for move in row
        )
        return no_winner and all(played_moves)