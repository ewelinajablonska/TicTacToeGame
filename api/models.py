from datetime import datetime
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
    title = models.CharField(max_length=5)
    address = models.CharField(max_length=255)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    phone = models.CharField(max_length=40, blank=True)


class HighScore(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(editable=False, blank=True)
    duration_time = models.TimeField(editable=False, blank=True)
    moves_count = models.IntegerField(default=1)