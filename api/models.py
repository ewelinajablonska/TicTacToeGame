from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from django.conf import settings


class User(AbstractUser):
    username = models.CharField(blank=True, null=True, max_length=60)
    email = models.EmailField(_("email address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    def __str__(self):
        return "{}".format(self.email)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    title = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=40, blank=True)

    def __str__(self) -> str:
        return "profile: {} ({})".format(self.title, self.user.email)


class HighScore(models.Model):
    player = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(editable=False, blank=True)
    duration_time = models.DurationField(blank=True)
    moves_count = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        """On save, update timestamps"""
        if not self.id:
            self.date = timezone.now()

        return super(HighScore, self).save(*args, **kwargs)


class Move(models.Model):
    row = models.IntegerField(blank=True, null=True)
    col = models.IntegerField(blank=True, null=True)
    player = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, blank=True, null=True
    )
    # time_stamp = models.DateTimeField(editable=False, blank=True)

    # def save(self, *args, **kwargs):
    #     """On save, update timestamps"""
    #     self.date = timezone.now()

    #     return super(Move, self).save(*args, **kwargs)

class Game(models.Model):
    # setup informations
    players = models.ManyToManyField(
        UserProfile, blank=True, related_name="game_players"
    )
    max_players_number = models.IntegerField(default=2)
    created_date = models.DateTimeField(blank=True)
    board_size = models.IntegerField(default=3)
    winning_combinations = models.JSONField(null=True, blank=True, default=list)
    # finish informations
    is_done = models.BooleanField(default=False)
    has_winner = models.BooleanField(default=False)
    winner_combination = models.JSONField(null=True, blank=True, default=list)
    # status = models.JSONField(null=True, blank=True, default=list)
    # current informations
    current_player = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="current_player",
    )
    current_moves = models.ForeignKey(
        Move, on_delete=models.CASCADE, blank=True, null=True
    )
